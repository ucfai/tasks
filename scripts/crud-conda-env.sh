#!/bin/sh

OS=`uname -r`

case $OS in
    "Darwin") path="macos" ;;
    "Linux")  path="linux" ;;
esac

#: grab the name of the admin environment's name
admin_name=`head -n 1 admin/env/${path}.yml | cut -f2 -d ' '`

#: update/create `conda` environment for the admin module
if conda env list | grep -q ${admin_name}; then
    conda env update -f admin/env/${path}.yml
else
    conda env create -f admin/env/${path}.yml
fi