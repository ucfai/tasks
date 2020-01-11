# Last Update: Jan 2020
FROM continuumio/miniconda3:4.7.12 as autobotbase

ADD env.yml /opt/env.yml

ARG env_name
# ENV ENV_NAME $(head -1 /opt/env.yml | cut -d ":" -f 2 | tr -d "[:space:]")
ENV ENV_NAME ${env_name}

ARG org_name="ucfai"
ENV ORG_NAME ${org_name}

ENV IN_DOCKER true

RUN conda env create -f /opt/env.yml

# ENV PATH /opt/conda/envs/${ENV_NAME}/bin:$PATH

RUN    env_name=$(head -1 /opt/env.yml | cut -d ":" -f 2 | tr -d "[:space:]") \
    && echo "conda activate ${ENV_NAME}" >> ~/.bashrc

WORKDIR /{{ ORG_NAME }}

ENTRYPOINT [ "/autobot/docker/entrypoint" ]

# Using `pip install -e .`
from autobotbase as development

ENV STAGE development

# RUN    git clone https://github.com/${ORG_NAME}/bot /autobot \
#     && conda activate ${env_name} \
#     && pip install -e /autobot

# Using `pip install git+https://github.com/ucfai/bot@master
from autobotbase as production

ENV STAGE production

# RUN    conda activate ${env_name} \
#     && pip install git+https://github.com/${ORG_NAME}/bot