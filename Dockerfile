FROM python:2.7
RUN pip install zmq
ADD . /code
WORKDIR /code
