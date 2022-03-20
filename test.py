import covalent as ct
from typing import List

@ct.electron(executor="braket")
def hybrid_task(size: int, shots: int, angles: List):
    import pennylane as qml
    import random

    device_arn = os.environ["AMZN_BRAKET_DEVICE_ARN"]
#    s3_dest = (os.environ["AMZN_BRAKET_OUT_S3_BUCKET"], "results")

    device = qml.device(
        "braket.aws.qubit", 
        device_arn=device_arn, 
#        s3_destination_folder=output_bucket, 
        wires=size,
        shots=shots,
        parallel=True,
        max_parallel=4,
    )

    @qml.qnode(device)
    def circuit(angles):
        for angle in angles:
            wire = random.randint(size)
            if random.random() < 0.5:
                qml.RX(angle, wires=wire)
            else:
                qml.RY(angle, wires=wire)

        return [qml.expval(qml.PauliZ(i)) for i in range(size)]

    result = circuit(angles)

    return result

@ct.lattice
def workflow(size: int, shots: int, angles: List):
    return hybrid_task(size, shots, angles)

if __name__ == "__main__":
    result = ct.dispatch_sync(workflow)(size=2, shots=100, angles=[0.2, 0.3, 0.4, 0.5])
    print(result)
