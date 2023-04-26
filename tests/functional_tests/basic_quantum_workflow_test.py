import os

import covalent as ct
import pytest
from braket.tracking import Tracker


@pytest.mark.functional_tests
def test_basic_quantum_workflow():
    @ct.electron(executor="braket")
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

    print(result_object)

    res, cost = result_object.result
    print("Result:", res)
    print("Cost:", cost)

    assert res == 0.0
