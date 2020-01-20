# Last Update: Jan 2020
FROM continuumio/miniconda3:4.7.12 as autobotbase

ADD env.yml /opt/env.yml

ARG env_name="autobot"
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

ENTRYPOINT [ "/docker/entrypoint" ]

# Using `pip install -e .`
FROM docker.pkg.github.com/ucfai/bot/env:latest as development

ENV STAGE development

# TODO properly sort out how to install `autobot` from pip and have it show-up
#      in the entrypoint (using a local install)

# Using `pip install git+https://github.com/ucfai/bot@master
FROM docker.pkg.github.com/ucfai/bot/env:latest as production

ENV STAGE production

# TODO properly sort out how to install `autobot` from pip and have it show-up
#      in the entrypoint (using a remote install)