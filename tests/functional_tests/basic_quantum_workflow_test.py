import os

import covalent as ct
import pytest
from braket.tracking import Tracker

from covalent_braket_plugin.braket import BraketExecutor

braket_executor = \
    BraketExecutor(
            region='us-east-1',
            s3_bucket_name='amazon-braket-cova-qa-covalent-svc-bucket',
            ecr_image_uri='927766187775.dkr.ecr.us-east-1.amazonaws.com/cova-qa-covalent-svc-images:braket',
            braket_job_execution_role_name='cova-qa-covalent-svc-braket-execution-role',
            quantum_device='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            classical_device='ml.m5.large',
            storage=30
        )

deps_pip = ct.DepsPip(packages=["pennylane"])

@pytest.mark.functional_tests
def test_basic_quantum_workflow():
    @ct.electron(executor=braket_executor, deps_pip=deps_pip)
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

    @ct.electron(deps_pip=deps_pip)
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
