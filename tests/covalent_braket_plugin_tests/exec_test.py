# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

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
