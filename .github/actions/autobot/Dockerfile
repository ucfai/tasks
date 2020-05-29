FROM continuumio/miniconda:4.7.12

ARG TASK_REPO="ionlights/ucfai-tasks"

COPY env.yml /env.yml
COPY entrypoint.sh /entrypoint.sh

RUN git clone https://github.com/${TASK_REPO} && \
    conda env create -f /env.yml

ENV PATH /opt/conda/envs/tasks/bin:$PATH

ENTRYPOINT [ "/entrypoint.sh" ]