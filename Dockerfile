# Last Update: Jan 2019
FROM ubuntu:18.04

ARG conda_vers=4.5.11

RUN apt-get update -y && \
    apt-get install -y wget

RUN    wget -o /opt/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-${conda_vers}-Linux-x86_64.sh \
    && chmod +x /opt/miniconda.sh \
    && sh /opt/miniconda.sh -b -p /opt/conda \
    && export PATH="/opt/conda/bin:$PATH"

ADD envs/linux.yml /opt/env.yml
RUN    conda env create -n ucfai python=3.7 \
    && conda env update -f /opt/env.yml \
    && export PATH="/opt/conda/envs/ucfai-admin/bin:$PATH"

ENTRYPOINT [ "ucfai" ]