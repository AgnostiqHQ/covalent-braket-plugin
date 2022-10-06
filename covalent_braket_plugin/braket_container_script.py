import json
import os
import pickle
from pathlib import Path

import boto3

# "covalent-{dispatch_id}-{node_id}"
job_name = os.environ.get("AMZN_BRAKET_JOB_NAME")

# {dispatch_id}-{node_id}
task_id = job_name[len("covalent-") :]

working_dir = "/opt/ml/code/workdir"
Path(working_dir).mkdir(parents=True, exist_ok=True)

meta_dir = os.environ.get("SM_CHANNEL_TASKMETADATA")
meta_file_path = os.path.join(meta_dir, f"metadata-{task_id}.json")

with open(meta_file_path, "r") as f:
    metadata = json.load(f)

input_object_key = metadata["input_object_key"]
output_object_key = metadata["output_object_key"]
s3_bucket = metadata["s3_bucket"]


FUNC_FILENAME = f"func-{task_id}.pkl"
RESULT_FILENAME = f"result-{task_id}.json"

local_func_filename = os.path.join(working_dir, FUNC_FILENAME)
local_result_filename = os.path.join(working_dir, RESULT_FILENAME)

s3 = boto3.client("s3")
s3.download_file(s3_bucket, input_object_key, local_func_filename)

with open(local_func_filename, "rb") as f:
    function, args, kwargs = pickle.load(f)

# Result is a TransportableObject
result = function(*args, **kwargs)

with open(local_result_filename, "w") as f:
    f.write(result.serialize_to_json())

s3.upload_file(local_result_filename, s3_bucket, output_object_key)
print(f"Uploaded result to s3://{s3_bucket}/{output_object_key}")
