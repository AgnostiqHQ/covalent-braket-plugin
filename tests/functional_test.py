from typing import List

import covalent as ct
from covalent._results_manager import Result


def test_executor_functional():
    @ct.electron(executor="braket")
    def hybrid_task(size: int, shots: int, angles: List):
        import os
        import random

        import pennylane as qml

        device_arn = os.environ["AMZN_BRAKET_DEVICE_ARN"]
        s3_bucket = os.environ["AMZN_BRAKET_OUT_S3_BUCKET"]
        s3_task_dir = os.environ["AMZN_BRAKET_TASK_RESULTS_S3_URI"].split(s3_bucket)[1]

        device = qml.device(
            "braket.aws.qubit",
            device_arn=device_arn,
            s3_destination_folder=(s3_bucket, s3_task_dir),
            wires=size,
            shots=shots,
            parallel=True,
            max_parallel=4,
        )

        @qml.qnode(device)
        def circuit(angles):
            for angle in angles:
                wire = random.randint(0, size - 1)
                if random.random() < 0.5:
                    qml.RX(angle, wires=wire)
                else:
                    qml.RY(angle, wires=wire)

            return [qml.expval(qml.PauliZ(i)) for i in range(size)]

        result = circuit(angles=angles)

        return result

    @ct.lattice
    def workflow(size: int, shots: int, angles: List):
        return hybrid_task(size, shots, angles)

    result = ct.dispatch_sync(workflow)(size=2, shots=100, angles=[0.2, 0.3, 0.4, 0.5])
    assert result.status == str(Result.COMPLETED)
