&nbsp;

<div align="center">

<img src="https://raw.githubusercontent.com/AgnostiqHQ/covalent-braket-plugin/main/assets/aws_braket_readme_banner.jpg" width=150%>

[![covalent](https://img.shields.io/badge/covalent-0.177.0-purple)](https://github.com/AgnostiqHQ/covalent)
[![python](https://img.shields.io/pypi/pyversions/covalent-braket-plugin)](https://github.com/AgnostiqHQ/covalent-braket-plugin)
[![tests](https://github.com/AgnostiqHQ/covalent-braket-plugin/actions/workflows/tests.yml/badge.svg)](https://github.com/AgnostiqHQ/covalent-braket-plugin/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/AgnostiqHQ/covalent-braket-plugin/branch/main/graph/badge.svg?token=QNTR18SR5H)](https://codecov.io/gh/AgnostiqHQ/covalent-braket-plugin)
[![agpl](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.en.html)

</div>

## Covalent Braket Hybrid Jobs Plugin

Covalent is a Pythonic workflow tool used to execute tasks on advanced computing hardware. This executor plugin interfaces Covalent with [AWS Braket Hybrid Jobs](https://docs.aws.amazon.com/braket/latest/developerguide/braket-jobs.html)
## Installing

To use this plugin with Covalent, install it with `pip`:
```
pip install covalent-braket-plugin
```

## Usage Example

The following workflow prepares a uniform superposition of the single-qubit standard basis states and measures it.

```python
import covalent as ct
from covalent_braket_plugin.braket import BraketExecutor
import os

# AWS resources to pass to the executor
credentials_file = "~/.aws/credentials"
profile = "default"
s3_bucket_name = "braket_s3_bucket"
ecr_image_uri = "111223344.dkr.ecr.us-east-1.amazonaws.com/amazon-braket-ecr-repo:latest"
iam_role_name = "covalent-braket-iam-role"

ex = BraketExecutor(
    profile=profile,
    credentials=credentials_file,
    s3_bucket_name=s3_bucket_name,
    ecr_image_uri=ecr_image_uri,
    braket_job_execution_role_name=iam_role_name,
    quantum_device="arn:aws:braket:::device/quantum-simulator/amazon/sv1",
    classical_device="ml.m5.large",
    storage=30,
    time_limit=300,
)


@ct.electron(executor=ex)
def simple_quantum_task(num_qubits: int):
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

    res = simple_circuit().numpy()
    return res


@ct.lattice
def simple_quantum_workflow(num_qubits: int):
    return simple_quantum_task(num_qubits=num_qubits)


dispatch_id = ct.dispatch(simple_quantum_workflow)(1)
result_object = ct.get_result(dispatch_id, wait=True)

# We expect 0 as the result
print("Result:", result_object.result)
```

To run such workflows, users must have AWS credentials allowing access
to Braket, ECR, S3, and some other services. These permissions must be
defined in an IAM Role (called `"covalent-braket-iam-role"` in this
example). The [AWS
documentation has more information about managing Braket
access](https://docs.aws.amazon.com/braket/latest/developerguide/braket-manage-access.html).

## Overview of Configuration

See the
[RTD](https://covalent.readthedocs.io/en/latest/api/executors/awsbraket.html)
for how to configure this executor.

## Required Cloud Resources

In order to run your workflows with covalent there are a few notable resources that need to be provisioned first. Particularly an S3 bucket must be created, an IAM role with the `AmazonBraketFullAccess` policy, and a private ECR repo with an uploaded image for the tasks to use.

For more information regarding which cloud resources need to be provisioned visit our read the docs [RTD](https://covalent.readthedocs.io/en/latest/api/executors/awsbraket.html) guide for this plugin.

## Release Notes

Release notes are available in the [Changelog](https://github.com/AgnostiqHQ/covalent-braket-plugin/blob/main/CHANGELOG.md).

## Citation

Please use the following citation in any publications:

> W. J. Cunningham, S. K. Radha, F. Hasan, J. Kanem, S. W. Neagle, and S. Sanand.
> *Covalent.* Zenodo, 2022. https://doi.org/10.5281/zenodo.5903364

## License

Covalent is licensed under the GNU Affero GPL 3.0 License. Covalent
may be distributed under other licenses upon request. See the
[LICENSE](https://github.com/AgnostiqHQ/covalent-braket-plugin/blob/main/LICENSE)
file or contact the [support team](mailto:support@agnostiq.ai) for
more details.
