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
[ $? ] && export PATH="/opt/conda/envs/tasks/bin:$PATH"

echo "inv -f /group/invoke.yml $commands"
inv -f /group/invoke.yml $commands > /output.txt
cat /output.txt

semester=$(grep -i semester /group/invoke.yml | cut -d " " -f 2)
echo "::set-output name=status::$(cat /output.txt)"
echo "::set-output name=semester::$semester"