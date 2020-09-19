FROM python:3.8.2-buster

RUN apt-get update
RUN pip install --upgrade pip

COPY . /src
WORKDIR /src

RUN pip install -Ue ".[dev]" -c constraints.txt

