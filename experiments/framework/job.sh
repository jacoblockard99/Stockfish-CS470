#!/bin/bash
#
#SBATCH --job-name=stockfish
#SBATCH --output={OUTPUT}
#SBATCH --time=1:00:00

srun ./play {ARGS}
