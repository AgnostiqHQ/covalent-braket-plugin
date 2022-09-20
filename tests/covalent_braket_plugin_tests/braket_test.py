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

"""Unit tests for AWS batch executor."""

import os
from base64 import b64encode
from typing import Dict, List
from unittest.mock import MagicMock

import cloudpickle
import pytest

from covalent_braket_plugin.braket import BraketExecutor
from covalent_braket_plugin.scripts import DOCKER_SCRIPT, PYTHON_EXEC_SCRIPT

MOCK_CREDENTIALS = "mock_credentials"
MOCK_PROFILE = "mock_profile"
MOCK_S3_BUCKET_NAME = "mock_s3_bucket_name"
MOCK_ECR_REPO_NAME = "mock_ecr_repo_name"
MOCK_BRAKET_JOB_EXECUTION_ROLE_NAME = "mock_role_name"
MOCK_QUANTUM_DEVICE = "mock_device"
MOCK_CLASSICAL_DEVICE = "mock_device"
MOCK_STORAGE = 1
MOCK_TIME_LIMIT = 1
MOCK_POLL_FREQ = 1


@pytest.fixture
def braket_executor(mocker):
    config_mock = mocker.patch("covalent_braket_plugin.braket.get_config")
    config_mock.return_value = "default"
    return BraketExecutor(
        credentials=MOCK_CREDENTIALS,
        profile=MOCK_PROFILE,
        s3_bucket_name=MOCK_S3_BUCKET_NAME,
        ecr_repo_name=MOCK_ECR_REPO_NAME,
        braket_job_execution_role_name=MOCK_BRAKET_JOB_EXECUTION_ROLE_NAME,
        quantum_device=MOCK_QUANTUM_DEVICE,
        classical_device=MOCK_CLASSICAL_DEVICE,
        storage=MOCK_STORAGE,
        time_limit=MOCK_TIME_LIMIT,
        poll_freq=MOCK_POLL_FREQ,
    )


def test_executor_init_default_values(braket_executor):
    """Test that the init values of the executor are set properly."""
    assert braket_executor.credentials_file == MOCK_CREDENTIALS
    assert braket_executor.profile == MOCK_PROFILE
    assert braket_executor.s3_bucket_name == MOCK_S3_BUCKET_NAME
    assert braket_executor.ecr_repo_name == MOCK_ECR_REPO_NAME
    assert braket_executor.execution_role == MOCK_BRAKET_JOB_EXECUTION_ROLE_NAME
    assert braket_executor.quantum_device == MOCK_QUANTUM_DEVICE
    assert braket_executor.classical_device == MOCK_CLASSICAL_DEVICE
    assert braket_executor.storage == MOCK_STORAGE
    assert braket_executor.time_limit == MOCK_TIME_LIMIT
    assert braket_executor.poll_freq == MOCK_POLL_FREQ


@pytest.mark.asyncio
async def test_run(braket_executor, mocker):
    """Test the run method."""

    def mock_func(x):
        return x

    mm = MagicMock()
    mocker.patch("covalent_braket_plugin.braket.boto3.Session", return_value=mm)
    package_and_upload_mock = mocker.patch(
        "covalent_braket_plugin.braket.BraketExecutor._package_and_upload"
    )
    poll_braket_job_mock = mocker.patch(
        "covalent_braket_plugin.braket.BraketExecutor._poll_braket_job"
    )
    query_result_mock = mocker.patch(
        "covalent_braket_plugin.braket.BraketExecutor._query_result", return_value=(1, "Hi", "")
    )
    task_metadata = {"dispatch_id": "mock_dispatch_id", "node_id": 1, "results_dir": "/tmp"}
    await braket_executor.run(
        function=mock_func, args=[], kwargs={"x": 1}, task_metadata=task_metadata
    )
    package_and_upload_mock.assert_called_once_with(
        mock_func,
        "mock_dispatch_id-1",
        "/tmp/mock_dispatch_id",
        "result-mock_dispatch_id-1.pkl",
        [],
        {"x": 1},
    )
    poll_braket_job_mock.assert_called_once()
    query_result_mock.assert_called_once()


def test_format_exec_script(braket_executor):
    """Test method that constructs the executable tasks-execution Python script."""
    kwargs = {
        "func_filename": "mock_function_filename",
        "result_filename": "mock_result_filename",
        "docker_working_dir": "mock_docker_working_dir",
    }
    exec_script = braket_executor._format_exec_script(**kwargs)
    assert exec_script == PYTHON_EXEC_SCRIPT.format(
        s3_bucket_name=braket_executor.s3_bucket_name, **kwargs
    )


def test_format_dockerfile(braket_executor):
    """Test method that constructs the dockerfile."""
    docker_script = braket_executor._format_dockerfile(
        exec_script_filename="root/mock_exec_script_filename",
        docker_working_dir="mock_docker_working_dir",
    )
    assert docker_script == DOCKER_SCRIPT.format(
        func_basename="mock_exec_script_filename", docker_working_dir="mock_docker_working_dir"
    )


def test_package_and_upload(braket_executor, mocker):
    class MockClient:
        def upload_file(self, filename, bucket_name, func_filename):
            return filename

    """Test the package and upload method."""
    boto3_mock = mocker.patch("covalent_braket_plugin.braket.boto3")
    format_exec_script_mock = mocker.patch(
        "covalent_braket_plugin.braket.BraketExecutor._format_exec_script", return_value=""
    )
    format_dockerfile_mock = mocker.patch(
        "covalent_braket_plugin.braket.BraketExecutor._format_dockerfile", return_value=""
    )
    get_ecr_info_mock = mocker.patch(
        "covalent_braket_plugin.braket.BraketExecutor._get_ecr_info",
        return_value=("", "", ""),
    )
    mocker.patch("covalent_braket_plugin.braket.shutil.copyfile")
    mm = MagicMock()
    tag_mock = MagicMock()
    mm.images.build.return_value = tag_mock, "logs"
    mm.login.return_value = {"IdentityToken": None, "Status": "Login Succeeded"}
    mocker.patch("covalent_braket_plugin.braket.docker.from_env", return_value=mm)

    braket_executor._package_and_upload(
        "mock_transportable_object",
        "mock_image_tag",
        "mock_task_results_dir",
        "mock_result_filename",
        [],
        {},
    )
    boto3_mock.Session().client().upload_file.assert_called_once()
    format_exec_script_mock.assert_called_once()
    format_dockerfile_mock.assert_called_once()
    get_ecr_info_mock.assert_called_once()


@pytest.mark.asyncio
async def test_get_status(braket_executor):
    """Test the get status method."""

    class MockBraket:
        def get_job(self, jobArn: str) -> Dict:
            if jobArn == "1":
                return {"status": "SUCCESS"}
            elif jobArn == "2":
                return {"status": "RUNNING"}

    status = await braket_executor.get_status(braket=MockBraket(), job_arn="1")
    assert status == "SUCCESS"

    status = await braket_executor.get_status(braket=MockBraket(), job_arn="2")
    assert status == "RUNNING"


@pytest.mark.asyncio
async def test_poll_braket_job(braket_executor, mocker):
    """Test the method to poll the batch job."""
    get_status_mock = mocker.patch(
        "covalent_braket_plugin.braket.BraketExecutor.get_status",
        side_effect=[
            "RUNNING",
            "SUCCEEDED",
            "RUNNING",
            "FAILED",
        ],
    )

    with pytest.raises(Exception):
        await braket_executor._poll_braket_job(braket=MagicMock(), job_arn="1")
    get_status_mock.assert_awaited()


def test_query_result(braket_executor, mocker):
    """Test the method to query the results."""

    def download_file(filename, bucket_name, func_filename):
        return filename

    def describe_log_streams(logGroupName, logStreamNamePrefix):
        print("******DESCRIBE LOG STREAMS********")
        print(logGroupName)
        print(logStreamNamePrefix)
        return {"logStreams": [{"logStreamName": f"{logStreamNamePrefix}-mock-name"}]}

    def get_log_events(logGroupName, logStreamName):
        return {"events": [{"message": "mock_logs"}]}

    boto3_mock = mocker.patch("covalent_braket_plugin.braket.boto3")
    boto3_client_mock = boto3_mock.Session().client()

    boto3_client_mock.download_file.side_effect = download_file
    boto3_client_mock.describe_log_streams.side_effect = describe_log_streams
    boto3_client_mock.get_log_events.side_effect = get_log_events

    task_results_dir, result_filename = "/tmp", "mock_result_filename.pkl"
    local_result_filename = os.path.join(task_results_dir, result_filename)
    with open(local_result_filename, "wb") as f:
        cloudpickle.dump("hello world", f)
    assert braket_executor._query_result(result_filename, task_results_dir, "1", None) == (
        "hello world",
        "mock_logs\n",
        "",
    )


@pytest.mark.asyncio
async def test_stubs(braket_executor):
    await braket_executor.cancel()
