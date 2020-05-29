#!/usr/bin/env bash

if [ "$#" -le 1 ]; then
    echo "You must provide a WORKDIR and COMMAND"
    exit 1
fi

workdir="$1"
commands="${@:2}"

cd /
ln -sf $wokdir /group

conda activate tasks

inv -f /group/invoke.yml $commands > /output.txt
cat /output.txt

echo "::set-output name=status::$(cat /output.txt)"