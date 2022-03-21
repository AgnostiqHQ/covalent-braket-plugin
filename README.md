&nbsp;

<div align="center">

![covalent logo](https://github.com/AgnostiqHQ/covalent/blob/master/doc/source/_static/dark.png#gh-dark-mode-only)
![covalent logo](https://github.com/AgnostiqHQ/covalent/blob/master/doc/source/_static/light.png#gh-light-mode-only)

&nbsp;

</div>

## Covalent Braket Hybrid Jobs Plugin

Covalent is a Pythonic workflow tool used to execute tasks on advanced computing hardware. This executor plugin interfaces Covalent with [AWS Braket Hybrid Jobs](https://docs.aws.amazon.com/braket/latest/developerguide/braket-jobs.html) by containerizing hybrid tasks and uploading them to the Elastic Container Registry. In order for workflows to be deployable, users must have AWS credentials allowing access to Braket, S3, ECR, and some other services. Users will need additional permissions to provision or manage cloud infrastructure used by this plugin.

To use this plugin with Covalent, clone this repository and install it using `pip`:

```
git clone git@github.com:AgnostiqHQ/covalent-braket-plugin.git
cd covalent-braket-plugin
pip install .
```

Users must add the correct entries to their Covalent [configuration](https://covalent.readthedocs.io/en/latest/how_to/config/customization.html) to support the Braket Hybrid Jobs plugin. Below is an example which works using some basic infrastructure created for testing purposes:

```console
[executors.braket]
credentials = "/home/user/.aws/credentials"
profile = ""
s3_bucket_name = "amazon-braket-covalent-job-resources"
ecr_repo_name = "covalent-braket-job-images"
cache_dir = "/tmp/covalent"
poll_freq = 30
braket_job_execution_role_name = "CovalentBraketJobsExecutionRole"
quantum_device = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
classical_device = "ml.m5.large"
storage = 30
time_limit = 300
```

Note that the S3 bucket must always start with `amazon-braket-` and the set of classical devices is constrained to [certain types](https://docs.aws.amazon.com/braket/latest/developerguide/braket-jobs-configure-job-instance-for-script.html).

Within a workflow, users can decorate electrons using these default settings:

```python
import covalent as ct

@ct.electron(executor="braket")
def my_hybrid_task(num_qubits: int, shots: int):
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
	shots=shots,
	parallel=True,
	max_parallel=4
    )

    @qml.qnode(device)
    def circuit():
        # Define the circuit here

    # Invoke the circuit and iterate as needed
```

or use a class object to customize the resources and other behavior:

```python
executor = ct.executor.BraketExecutor(
    classical_device = "ml.p3.2xlarge" # Includes a V100 GPU and 8 vCPUs
    quantum_device = "arn:aws:braket:::device/qpu/rigetti/Aspen-11", # 47-qubit QPU
    time_limit = 600, # 10-minute time limit
)
def my_custom_hybrid_task():
    # Task definition goes here
```

For more information about how to get started with Covalent, check out the project [homepage](https://github.com/AgnostiqHQ/covalent) and the official [documentation](https://covalent.readthedocs.io/en/latest/).

## Release Notes

Release notes are available in the [Changelog](https://github.com/AgnostiqHQ/covalent-braket-plugin/blob/main/CHANGELOG.md).

## Citation

Please use the following citation in any publications:

> W. J. Cunningham, S. K. Radha, F. Hasan, J. Kanem, S. W. Neagle, and S. Sanand.
> *Covalent.* Zenodo, 2022. https://doi.org/10.5281/zenodo.5903364

## License

Covalent is licensed under the GNU Affero GPL 3.0 License. Covalent may be distributed under other licenses upon request. See the [LICENSE](https://github.com/AgnostiqHQ/covalent-braket-plugin/blob/main/LICENSE) file or contact the [support team](mailto:support@agnostiq.ai) for more details.
