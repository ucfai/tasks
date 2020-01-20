FROM docker.pkg.github.com/ucfai/bot/base:latest

ENV STAGE production

# Using `pip install git+https://github.com/ucfai/bot@master
# TODO properly sort out how to install `autobot` from pip and have it show-up
#      in the entrypoint (using a remote install)