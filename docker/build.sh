#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <image name>"
    exit 1
fi

tag=$1

sudo docker build --no-cache -t wesleymonte/provider-service:${tag} -f docker/Dockerfile .