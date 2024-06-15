#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh
conda activate social
CUDA_VISIBLE_DEVICES=7 python /hhome/nlp2_g05/social_inovation/img2text.py $1 $2