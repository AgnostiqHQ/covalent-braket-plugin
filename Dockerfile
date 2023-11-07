ARG COVALENT_BASE_IMAGE
FROM ${COVALENT_BASE_IMAGE}

ARG COVALENT_PACKAGE_VERSION
ARG PRE_RELEASE

RUN apt-get update && apt-get install -y \
  rsync \
  gcc \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade \
  amazon-braket-pennylane-plugin>=1.17.4 \
  boto3>=1.28.5 \
  pennylane>=0.31.1 \
  sagemaker-training

RUN if [ -z "$PRE_RELEASE" ]; then \
  pip install "$COVALENT_PACKAGE_VERSION"; else \
  pip install --pre "$COVALENT_PACKAGE_VERSION"; \
  fi

WORKDIR /opt/ml/code
COPY covalent_braket_plugin/exec.py /opt/ml/code
ENV SAGEMAKER_PROGRAM /opt/ml/code/exec.py
