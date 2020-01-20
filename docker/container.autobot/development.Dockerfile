FROM docker.pkg.github.com/ucfai/bot/base:latest

ENV STAGE development

# Using `pip install -e .`
# TODO properly sort out how to install `autobot` from pip and have it show-up
#      in the entrypoint (using a local install)