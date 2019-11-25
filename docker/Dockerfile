FROM python

WORKDIR /service

RUN apt -y update

RUN apt install -y software-properties-common

RUN echo | apt-add-repository ppa:ansible/ansible

RUN apt install -y ansible

RUN pip3 install flask filelock

COPY ["api.py", "pool.py", "util.py", "/service/"]

COPY "worker-deployment" "/service/worker-deployment"

RUN mkdir storage keys

COPY ./storage/empty-pools.json ./storage/pools.json

ENTRYPOINT ["python3", "/service/api.py"]