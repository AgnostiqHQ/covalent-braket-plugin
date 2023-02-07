import covalent as ct
import pytest

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

@pytest.mark.functional_tests
def test_basic_workflow():
    @ct.electron(executor=braket_executor)
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
