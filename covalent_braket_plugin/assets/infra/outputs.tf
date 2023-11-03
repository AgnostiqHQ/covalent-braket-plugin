# Copyright 2023 Agnostiq Inc.
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

output "braket_job_execution_role_name" {
  value       = aws_iam_role.braket_iam_role.id
  description = "Allocated IAM role name"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.braket_bucket.id
  description = "Allocated AWS S3 bucket name for storing lambda files"
}

output "ecr_image_uri" {
  value       = "${aws_ecr_repository.braket_ecr_repo.repository_url}:${var.executor_base_image_tag_name}"
  description = "Allocated ECR repo name"
}
