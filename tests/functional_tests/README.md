## Functional Test Instructions

### 1.Setup

In the project root run the following:

```sh
pip install -r ./tests/requirements.txt
pip install -r ./tests/functional_tests/requirements.txt
export PYTHONPATH=$(pwd)
```

Fill in the configuration values for the Braket executor either manually or from Terraform output.

### 2. Run Functional Tests

```sh
pytest -vvs -m functional_tests
```
