ARG COVALENT_BASE_IMAGE
FROM ${COVALENT_BASE_IMAGE}

RUN apt-get update && apt-get install -y \
  rsync \
  gcc \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --use-feature=in-tree-build --upgrade \
  amazon-braket-pennylane-plugin==1.6.9 \
  boto3==1.20.48 \
  cloudpickle==2.0.0 \
  pennylane==0.24.0 \
  sagemaker-training

WORKDIR /opt/ml/code

COPY covalent_braket_plugin/exec.py /opt/ml/code
ENV SAGEMAKER_PROGRAM exec.py
