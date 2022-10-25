import os

import boto3
import cloudpickle as pickle

s3_bucket_name = os.environ.get("SM_HP_S3_BUCKET_NAME")
result_filename = os.environ.get("SM_HP_RESULT_FILENAME")
func_filename = os.environ.get("SM_HP_COVALENT_TASK_FUNC_FILENAME")
work_dir = os.environ.get("SM_HP_WORKDIR", "/opt/ml/code")

print(f"Covalent artifact s3 bucket: {s3_bucket_name}")
print(f"Result filename: {result_filename}")
print(f"Function filename: {func_filename}")

local_func_filename = os.path.join(work_dir, func_filename)
local_result_filename = os.path.join(work_dir, result_filename)

s3 = boto3.client("s3")
s3.download_file(s3_bucket_name, func_filename, local_func_filename)

with open(local_func_filename, "rb") as f:
    function, args, kwargs = pickle.load(f)

result = function(*args, **kwargs)

with open(local_result_filename, "wb") as f:
    pickle.dump(result, f)

s3.upload_file(local_result_filename, s3_bucket_name, result_filename)
