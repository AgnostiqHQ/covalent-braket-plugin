# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for AWS batch executor braket execution file."""

import os
import sys
from unittest import mock

import cloudpickle
from anyio import Path


def test_execution(mocker, tmp_path: Path):
    boto3_mock = mock.MagicMock()
    sys.modules["boto3"] = boto3_mock

    def mock_function(x):
        return x

    tmp_pickle_file = tmp_path / "mock_file.pkl"

    mocker.patch.dict(
        os.environ,
        {
            "SM_HP_S3_BUCKET_NAME": "mock_s3_bucket",
            "SM_HP_RESULT_FILENAME": "result_file.pkl",
            "SM_HP_COVALENT_TASK_FUNC_FILENAME": "mock_file.pkl",
            "SM_HP_WORKDIR": str(tmp_pickle_file.parent),
        },
    )

    with open(str(tmp_pickle_file), "wb") as f:
        x = 1
        positional_args = [x]
        cloudpickle.dump((mock_function, positional_args, {}), f)

    import covalent_braket_plugin.exec
