#!/bin/bash

sudo docker run hello-world > /dev/null 2> /dev/null

ENGINE_TEST=$?
if [ $ENGINE_TEST -eq 0 ]; then
    echo "The Docker Engine is ok"
    curl http://localhost:5555/info > /dev/null 2> /dev/null
    API_TEST=$?
    if [ $API_TEST -eq 0 ]; then
        echo "The worker is all right"
    else
        echo "Docker API is not opened"
        exit 1
    fi
else 
    echo "Docker Engine is not installed correctly"
    exit 1
fi