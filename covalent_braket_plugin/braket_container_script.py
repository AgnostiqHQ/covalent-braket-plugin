import os

import boto3
import cloudpickle as pickle

input_dir = os.environ.get("AMZN_BRAKET_INPUT_DIR")
output_dir = os.environ.get("AMZN_BRAKET_JOB_RESULTS_DIR")

FUNC_FILENAME = "input.pkl"
RESULT_FILENAME = "result.json"

local_func_filename = os.path.join("{input_dir}", "{FUNC_FILENAME}")
local_result_filename = os.path.join("{output_dir}", "{RESULT_FILENAME}")

with open(local_func_filename, "rb") as f:
    function, args, kwargs = pickle.load(f)

# Result is a TransportableObject
result = function(*args, **kwargs)

with open(local_result_filename, "w") as f:
    f.write(result.serialize_to_json())
