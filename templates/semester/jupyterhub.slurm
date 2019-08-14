#!/bin/bash
#SBATCH --job-name=%u
#SBATCH --output=sigai-%j.log
#SBATCH --ntasks=1
#SBATCH --mem=8gb
#SBATCH --time=02:00:00

date;hostname;pwd

export XDG_RUNTIME_DIR=${TMPDIR}

source activate sigai-fa18

jupyter hub --no-browser --port=$1 --ip='0.0.0.0' --NotebookApp.token=''

date
