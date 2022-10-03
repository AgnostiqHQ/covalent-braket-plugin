FROM public.ecr.aws/covalent/covalent:latest

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --use-feature=in-tree-build --upgrade \
  amazon-braket-pennylane-plugin==1.6.9 \
  boto3==1.20.48 \
  cloudpickle==2.0.0 \
  pennylane==0.24.0 \
  sagemaker-training
RUN pip install covalent

WORKDIR /opt/ml/code

COPY covalent_braket_plugin/braket_container_script.py /opt/ml/code
ENV SAGEMAKER_PROGRAM braket_container_script.py
ENTRYPOINT []
