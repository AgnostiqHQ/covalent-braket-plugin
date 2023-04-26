import covalent as ct
import pytest


@pytest.mark.functional_tests
def test_basic_workflow():
    @ct.electron(executor="braket")
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
    print(result_object)
    print("Actual result:", result_object.result)
    print("Expected result:", "Hello, World!")

    assert result_object.result == "Hello, World!"
