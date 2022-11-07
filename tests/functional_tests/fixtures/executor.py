from dotenv import load_dotenv

load_dotenv()

import os

from covalent_braket_plugin.braket import BraketExecutor

executor_config = {
    "ecr_image_uri": os.getenv("executor_ecr_image_uri"),
    "s3_bucket_name": os.getenv("executor_s3_bucket_name"),
    "braket_job_execution_role_name": os.getenv("executor_braket_job_execution_role_name"),
    "quantum_device": os.getenv(
        "executor_quantum_device", "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
    ),
    "classical_device": os.getenv("executor_classical_device", "ml.m5.large"),
    "cache_dir": os.getenv("executor_cache_dir", "/tmp/covalent"),
    "poll_freq": os.getenv("executor_poll_freq", 5),
    "time_limit": os.getenv("executor_time_limit", 300),
    "storage": os.getenv("executor_storage", 30),
}

print("Executor configuration:")
print(executor_config)

executor = BraketExecutor(**executor_config)
