import json
import os

import boto3
import cloudpickle as pickle

AMZN_BRAKET_HP_FILE = os.environ.get("AMZN_BRAKET_HP_FILE")

# read environment variables
with open(AMZN_BRAKET_HP_FILE, "r") as f:
    hyperparams = json.load(f)
    print("Hyperparams:")
    print(hyperparams)
    func_filename = hyperparams["COVALENT_TASK_FUNC_FILENAME"]
    result_filename = hyperparams["RESULT_FILENAME"]
    s3_bucket_name = hyperparams["S3_BUCKET_NAME"]

local_func_filename = os.path.join("/opt/ml/code", "{func_filename}")
local_result_filename = os.path.join("/opt/ml/code", "{result_filename}")

print(f"local_func_filename: {local_func_filename}")
print(f"local_result_filename: {local_result_filename}")

s3 = boto3.client("s3")
s3.download_file("{s3_bucket_name}", "{func_filename}", local_func_filename)

with open(local_func_filename, "rb") as f:
    function, args, kwargs = pickle.load(f)

result = function(*args, **kwargs)

with open(local_result_filename, "wb") as f:
    pickle.dump(result, f)

s3.upload_file(local_result_filename, "{s3_bucket_name}", "{result_filename}")
