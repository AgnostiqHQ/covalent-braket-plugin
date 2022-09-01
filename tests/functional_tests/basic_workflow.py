import json
import os
import subprocess

import covalent as ct

from covalent_braket_plugin.braket import BraketExecutor

terraform_dir = os.getenv("TF_DIR")

proc = subprocess.run(
    [
        "terraform",
        f"-chdir={terraform_dir}",
        "output",
        "-json",
    ],
    check=True,
    capture_output=True,
)

s3_bucket_name = json.loads(proc.stdout.decode())["s3_bucket_name"]["value"]
ecr_repo_name = json.loads(proc.stdout.decode())["ecr_repo_name"]["value"]
iam_role_name = json.loads(proc.stdout.decode())["iam_role_name"]["value"]

credentials_file = os.getenv("AWS_SHARED_CREDENTIALS_FILE")
profile = os.getenv("AWS_PROFILE")

ex = BraketExecutor(
    credentials=credentials_file,
    profile=profile,
    s3_bucket_name=s3_bucket_name,
    ecr_repo_name=ecr_repo_name,
    braket_job_execution_role_name=iam_role_name,
    cache_dir="/tmp/covalent",
    poll_freq=30,
    quantum_device="arn:aws:braket:::device/quantum-simulator/amazon/sv1",
    classical_device="ml.m5.large",
    storage=30,
    time_limit=300,
)


@ct.electron(executor=ex)
def join_words(a, b):
    return ", ".join([a, b])


@ct.electron(executor="local")
def excitement(a):
    return f"{a}!"


# Construct a workflow of tasks
@ct.lattice(executor="local")
def simple_workflow(a, b):
    phrase = join_words(a, b)
    return excitement(phrase)


dispatch_id = ct.dispatch(simple_workflow)("Hello", "World")

result_object = ct.get_result(dispatch_id, wait=True)
print("Actual result:", result_object.result)
print("Expected result:", "Hello, World!")

assert result_object.result == "Hello, World!"
