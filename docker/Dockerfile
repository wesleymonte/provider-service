FROM python

WORKDIR /service

RUN pip3 install flask

RUN pip3 install filelock

COPY ["api.py", "pool.py", "util.py", "/service/"]

RUN mkdir storage keys

COPY ./storage/empty-pools.json ./storage/pools.json

ENTRYPOINT ["python3", "/service/api.py"]