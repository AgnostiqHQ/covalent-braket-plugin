import json
import os
import subprocess

import covalent as ct
from braket.tracking import Tracker

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
    classical_device="ml.m5.xlarge",
    storage=30,
    time_limit=300,
)


@ct.electron(executor=ex)
def my_hybrid_task(num_qubits: int):
    import pennylane as qml

    # These are passed to the Hybrid Jobs container at runtime
    device_arn = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    s3_bucket = os.environ["AMZN_BRAKET_OUT_S3_BUCKET"]
    s3_task_dir = os.environ["AMZN_BRAKET_TASK_RESULTS_S3_URI"].split(s3_bucket)[1]

    device = qml.device(
        "braket.aws.qubit",
        device_arn=device_arn,
        s3_destination_folder=(s3_bucket, s3_task_dir),
        wires=num_qubits,
    )

    @qml.qnode(device=device)
    def simple_circuit():
        qml.Hadamard(wires=[0])
        return qml.expval(qml.PauliZ(wires=[0]))

    with Tracker() as tracker:
        res = simple_circuit().numpy()
    return res, tracker


@ct.electron
def get_cost(tracker: Tracker):
    return tracker.simulator_tasks_cost()


@ct.lattice
def simple_quantum_workflow(num_qubits: int):
    res, tracker = my_hybrid_task(num_qubits=num_qubits)
    cost = get_cost(tracker)
    return res, cost


dispatch_id = ct.dispatch(simple_quantum_workflow)(1)
print("Dispatch id:", dispatch_id)
result_object = ct.get_result(dispatch_id, wait=True)

res, cost = result_object.result
print("Result:", res)
print("Cost:", cost)

assert res == 0.0
