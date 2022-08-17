&nbsp;

<div align="center">

<img src="https://raw.githubusercontent.com/AgnostiqHQ/covalent-braket-plugin/main/assets/aws_braket_readme_banner.jpg" width=150%>

</div>

## Covalent Braket Hybrid Jobs Plugin

Covalent is a Pythonic workflow tool used to execute tasks on advanced computing hardware. This executor plugin interfaces Covalent with [AWS Braket Hybrid Jobs](https://docs.aws.amazon.com/braket/latest/developerguide/braket-jobs.html) by containerizing hybrid tasks and uploading them to the Elastic Container Registry.

In order for workflows to be deployable, users must have AWS credentials allowing access to Braket, S3, ECR, and some other services. Users will need additional permissions to provision or manage cloud infrastructure used by this plugin. These permissions must be defined in an IAM Role with the name CovalentBraketJobsExecutionRole. [An example of the permissions that must be attached to the role can be found here](infra/iam/CovalentBraketJobsExecutionPolicy.json). [AWS documentation has more information about managing Braket access](https://docs.aws.amazon.com/braket/latest/developerguide/braket-manage-access.html).

To use this plugin with Covalent, clone this repository and install it using `pip`:

```
git clone git@github.com:AgnostiqHQ/covalent-braket-plugin.git
cd covalent-braket-plugin
pip install .
```

You need to have the AWS cli installed and configured. Covalent relies on the AWS credentials file that is created by the CLI.

```
pip install awscli
aws configure
```

Set the environment variable `BRAKET_JOB_IMAGES` to some name for where your images will be stored, for example `my-braket-images`. Then create the repository.
```
aws ecr create-repository --repository-name $BRAKET_JOB_IMAGES
```

Set the environment variable `BRAKET_COVALENT_S3` to some name for where your pickle files and Braket results will be stored on the cloud. *The name _must_ begin with `amazon-braket`*. For example `amazon-braket-my-bucket`. Then create the bucket.
```
aws s3api create-bucket --bucket $BRAKET_COVALENT_S3 --region us-east-1
```

After starting Covalent, a section is added to the Covalent [configuration](https://covalent.readthedocs.io/en/latest/how_to/config/customization.html) to support the Braket Hybrid Jobs plugin. Below is an example which works using some basic infrastructure created for testing purposes:

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

These values may be customized. Note that the set of classical devices is constrained to [certain types](https://docs.aws.amazon.com/braket/latest/developerguide/braket-jobs-configure-job-instance-for-script.html).

Finally, [Docker engine](https://docs.docker.com/engine/install/) must be installed and running before dispatching a workflow using this plugin.

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

### Note :bulb:

If the script fails quickly, check `covalent logs`. If there is an ERROR in the logs, it should include helpful output on what you need to do to get it to run, for example

```
ERROR - Exception occurred when running task 3: There was an error uploading the Docker image to ECR.
This may be resolved by removing ~/.docker/config.json and trying your dispatch again.
For more information, see
https://stackoverflow.com/a/55103262/5513030
https://docs.aws.amazon.com/AmazonECR/latest/userguide/getting-started-cli.html
denied: Your authorization token has expired. Reauthenticate and try again.
```

## Release Notes

Release notes are available in the [Changelog](https://github.com/AgnostiqHQ/covalent-braket-plugin/blob/main/CHANGELOG.md).

## Citation

Please use the following citation in any publications:

> W. J. Cunningham, S. K. Radha, F. Hasan, J. Kanem, S. W. Neagle, and S. Sanand.
> *Covalent.* Zenodo, 2022. https://doi.org/10.5281/zenodo.5903364

## License

Covalent is licensed under the GNU Affero GPL 3.0 License. Covalent may be distributed under other licenses upon request. See the [LICENSE](https://github.com/AgnostiqHQ/covalent-braket-plugin/blob/main/LICENSE) file or contact the [support team](mailto:support@agnostiq.ai) for more details.
