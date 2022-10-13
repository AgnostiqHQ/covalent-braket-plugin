# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

"""AWS Braket Hybrid Jobs executor plugin for the Covalent dispatcher."""

import asyncio
import base64
import json
import os
import shutil
import sys
import tempfile
import time
from functools import partial
from pathlib import Path
from pprint import pprint
from typing import Any, Callable, Dict, List, Tuple

import boto3
import botocore
import cloudpickle as pickle
import docker
from covalent._shared_files.config import get_config
from covalent._shared_files.logger import app_log
from covalent._workflow.transport import TransportableObject
from covalent_aws_plugins import AWSExecutor

ECR_REPO_URI = "public.ecr.aws/covalent/covalent-braket-executor:latest"

_EXECUTOR_PLUGIN_DEFAULTS = {
    "credentials": os.environ.get("AWS_SHARED_CREDENTIALS_FILE")
    or os.path.join(os.environ["HOME"], ".aws/credentials"),
    "profile": os.environ.get("AWS_PROFILE") or "default",
    "s3_bucket_name": os.environ.get("BRAKET_COVALENT_S3")
    or "amazon-braket-covalent-job-resources",
    "braket_job_execution_role_name": "CovalentBraketJobsExecutionRole",
    "quantum_device": "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
    "classical_device": "ml.m5.large",
    "storage": 30,
    "time_limit": 300,
    "cache_dir": "/tmp/covalent",
    "poll_freq": 30,
}

executor_plugin_name = "BraketExecutor"


class BraketExecutorDockerException(Exception):
    def __init__(self, status, repo):
        self.message = (
            "There was an error uploading the Docker image to ECR.\n"
            + f"Check that the repo {repo} exists.\n"
            + "This may also be resolved by removing ~/.docker/config.json and trying your dispatch again.\n"
            + "For more information, see\n"
            + "https://stackoverflow.com/a/55103262/5513030\n"
            + "https://docs.aws.amazon.com/AmazonECR/latest/userguide/getting-started-cli.html\n"
            + status
        )
        super().__init__(self.message)


class BraketExecutor(AWSExecutor):
    """AWS Braket Hybrid Jobs executor plugin class."""

    def __init__(
        self,
        s3_bucket_name: str = None,
        braket_job_execution_role_name: str = None,
        classical_device: str = None,
        storage: int = None,
        time_limit: int = None,
        poll_freq: int = None,
        quantum_device: str = None,
        profile: str = None,
        credentials: str = None,
        cache_dir: str = None,
        region: str = None,
        **kwargs,
    ):

        # we exclude region from get_config as we want AWSExecutor to properly treat cases where it's not explicitly defined.
        credentials = credentials or get_config("executors.braket.credentials")
        profile = profile or get_config("executors.braket.profile")
        s3_bucket_name = s3_bucket_name or get_config("executors.braket.s3_bucket_name")
        braket_job_execution_role_name = braket_job_execution_role_name or get_config(
            "executors.braket.braket_job_execution_role_name"
        )
        s3_bucket_name = s3_bucket_name or get_config("executors.braket.s3_bucket_name")
        cache_dir = cache_dir or get_config("executors.braket.cache_dir")
        time_limit = time_limit or get_config("executors.braket.time_limit")
        poll_freq = poll_freq or get_config("executors.braket.poll_freq")

        super().__init__(
            credentials_file=credentials,
            profile=profile,
            s3_bucket_name=s3_bucket_name,
            execution_role=braket_job_execution_role_name,
            region=region,
            cache_dir=cache_dir,
            time_limit=time_limit,
            poll_freq=poll_freq,
            **kwargs,
        )

        self.quantum_device = quantum_device or get_config("executors.braket.quantum_device")
        self.classical_device = classical_device or get_config("executors.braket.classical_device")
        self.storage = storage or get_config("executors.braket.storage")

    async def _upload_task(
        self, function: Callable, args: List, kwargs: Dict, upload_metadata: Dict
    ):
        """
        Abstract method that uploads the pickled function to the remote cache.
        """
        image_tag = upload_metadata["image_tag"]

        loop = asyncio.get_running_loop()

        fut = loop.run_in_executor(
            None,
            self._package_and_upload,
            function,
            image_tag,
            args,
            kwargs,
        )
        return await fut

    async def submit_task(self, submit_metadata: Dict) -> Any:
        """
        Abstract method that invokes the task on the remote backend.

        Args:
            task_metadata: Dictionary of metadata for the task. Current keys are
                          `dispatch_id` and `node_id`.
        Return:
            task_uuid: Task UUID defined on the remote backend.
        """
        braket = boto3.Session(**self.boto_session_options()).client("braket")

        image_tag = submit_metadata["image_tag"]
        result_filename = submit_metadata["result_filename"]
        image_tag = submit_metadata["image_tag"]
        account = submit_metadata["account"]

        func_filename = f"func-{image_tag}.pkl"
        args = {
            "hyperParameters": {
                "COVALENT_TASK_FUNC_FILENAME": func_filename,
                "RESULT_FILENAME": result_filename,
                "S3_BUCKET_NAME": self.s3_bucket_name,
            },
            "algorithmSpecification": {
                "containerImage": {
                    "uri": ECR_REPO_URI,
                },
            },
            "checkpointConfig": {
                "s3Uri": f"s3://{self.s3_bucket_name}/checkpoints/{image_tag}",
            },
            "deviceConfig": {
                "device": self.quantum_device,
            },
            "instanceConfig": {
                "instanceType": self.classical_device,
                "volumeSizeInGb": self.storage,
            },
            "jobName": f"covalent-{image_tag}",
            "outputDataConfig": {
                "s3Path": f"s3://{self.s3_bucket_name}/braket/{image_tag}",
            },
            "roleArn": f"arn:aws:iam::{account}:role/{self.execution_role}",
            "stoppingCondition": {
                "maxRuntimeInSeconds": self.time_limit,
            },
        }

        app_log.debug("Using job args:")
        app_log.debug(args)
        try:
            job = braket.create_job(**args)

        except botocore.exceptions.ClientError as error:
            app_log.debug(error.response)
            raise error

        return job["jobArn"]

    async def _poll_task(self, poll_metadata: Dict) -> Any:
        """
        Abstract method that polls the remote backend until the status of a workflow's execution
        is either COMPLETED or FAILED.
        """
        braket = boto3.Session(**self.boto_session_options()).client("braket")
        job_arn = poll_metadata["job_arn"]
        loop = asyncio.get_running_loop()
        await self._poll_braket_job(braket, job_arn)

    async def query_result(self, query_metadata: Dict) -> Any:
        """
        Abstract method that retrieves the pickled result from the remote cache.
        """

        result_filename = query_metadata["result_filename"]
        task_results_dir = query_metadata["task_results_dir"]
        job_arn = query_metadata["job_arn"]
        image_tag = query_metadata["image_tag"]

        loop = asyncio.get_running_loop()
        fut = loop.run_in_executor(
            None,
            self._query_result,
            result_filename,
            task_results_dir,
            job_arn,
            image_tag,
        )
        output, stdout, stderr = await fut
        return output, stdout, stderr

    async def cancel(self) -> bool:
        """
        Abstract method that sends a cancellation request to the remote backend.
        """
        pass

    async def run(self, function: Callable, args: List, kwargs: Dict, task_metadata: Dict):

        dispatch_id = task_metadata["dispatch_id"]
        node_id = task_metadata["node_id"]
        results_dir = task_metadata["results_dir"]

        result_filename = f"result-{dispatch_id}-{node_id}.pkl"
        task_results_dir = os.path.join(results_dir, dispatch_id)
        image_tag = f"{dispatch_id}-{node_id}"

        # AWS Account Retrieval
        identity = self._validate_credentials(raise_exception=True)
        account = identity.get("Account")

        # TODO: Move this to BaseExecutor
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

        upload_task_metadata = {
            "image_tag": image_tag,
        }

        await self._upload_task(function, args, kwargs, upload_task_metadata)

        submit_metadata = {
            "image_tag": image_tag,
            "account": account,
            "task_results_dir": task_results_dir,
            "result_filename": result_filename,
        }

        app_log.debug("Submit metadata:")
        app_log.debug(submit_metadata)

        job_arn = await self.submit_task(submit_metadata)

        poll_metadata = {"job_arn": job_arn}

        await self._poll_task(poll_metadata)

        query_metadata = {
            "result_filename": result_filename,
            "task_results_dir": task_results_dir,
            "job_arn": job_arn,
            "image_tag": image_tag,
        }

        output, stdout, stderr = await self.query_result(query_metadata)

        print(stdout, end="", file=sys.stdout)
        print(stderr, end="", file=sys.stderr)

        return output

    def _package_and_upload(
        self,
        function: TransportableObject,
        image_tag: str,
        args: List,
        kwargs: Dict,
    ) -> str:
        """Package a task using Docker and upload it to AWS ECR.

        Args:
            function: A callable Python function.
            image_tag: Tag used to identify the Docker image.
            task_results_dir: Local directory where task results are stored.
            result_filename: Name of the pickled result.
            args: Positional arguments consumed by the task.
            kwargs: Keyword arguments consumed by the task.

        """
        app_log.debug("_package_and_upload")
        app_log.debug(self.s3_bucket_name)

        func_filename = f"func-{image_tag}.pkl"

        with tempfile.NamedTemporaryFile(dir=self.cache_dir) as function_file:
            # Write serialized function to file
            pickle.dump((function, args, kwargs), function_file)
            function_file.flush()

            # Upload pickled function to S3
            s3 = boto3.Session(**self.boto_session_options()).client("s3")
            s3.upload_file(function_file.name, self.s3_bucket_name, func_filename)

    async def get_status(self, braket, job_arn: str) -> str:
        """Query the status of a previously submitted Braket hybrid job.

        Args:
            braket: Braket client object.
            job_arn: ARN used to identify a Braket hybrid job.

        Returns:
            status: String describing the job status.
        """

        loop = asyncio.get_running_loop()
        get_job_callable = partial(braket.get_job, jobArn=job_arn)
        job = await loop.run_in_executor(None, get_job_callable)
        status = job["status"]

        return status

    async def _poll_braket_job(self, braket, job_arn: str) -> None:
        """Poll a Braket hybrid job until completion.

        Args:
            braket: Braket client object.
            job_arn: ARN used to identify a Braket hybrid job.

        Returns:
            None
        """

        status = await self.get_status(braket, job_arn)

        loop = asyncio.get_running_loop()
        while status not in ["COMPLETED", "FAILED", "CANCELLED"]:
            await asyncio.sleep(self.poll_freq)
            status = await self.get_status(braket, job_arn)

        if status == "FAILED":
            get_job_callable = partial(braket.get_job, jobArn=job_arn)
            job = await loop.run_in_executor(None, get_job_callable)
            failure_reason = job["failureReason"]
            raise Exception(failure_reason)

    def _query_result(
        self, result_filename: str, task_results_dir: str, job_arn: str, image_tag: str
    ) -> Tuple[Any, str, str]:
        """Query and retrieve a completed job's result.

        Args:
            result_filename: Name of the pickled result file.
            task_results_dir: Local directory where task results are stored.
            job_arn: Identifier used to identify a Braket hybrid job.
            image_tag: Tag used to identify the log file.

        Returns:
            result: The task's result, as a Python object.
            logs: The stdout and stderr streams corresponding to the task.
            empty_string: A placeholder empty string.
        """

        local_result_filename = os.path.join(task_results_dir, result_filename)

        s3 = boto3.Session(**self.boto_session_options()).client("s3")
        s3.download_file(self.s3_bucket_name, result_filename, local_result_filename)

        with open(local_result_filename, "rb") as f:
            result = pickle.load(f)
        os.remove(local_result_filename)

        logs = boto3.Session(**self.boto_session_options()).client("logs")

        log_group_name = "/aws/braket/jobs"
        log_stream_prefix = f"covalent-{image_tag}"
        log_stream_name = logs.describe_log_streams(
            logGroupName=log_group_name, logStreamNamePrefix=log_stream_prefix
        )["logStreams"][0]["logStreamName"]

        # TODO: This should be paginated, but the command doesn't support boto3 pagination
        # Up to 10000 log events can be returned from a single call to get_log_events()
        events = logs.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
        )["events"]

        log_events = ""
        for event in events:
            log_events += event["message"] + "\n"

        return result, log_events, ""
