FROM python:3.8

# ---------------
# Install the app
# ---------------

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.8 get-pip.py
RUN pip3 install --upgrade pip

WORKDIR /src

# Hack to avoid docker reinstalling every build
COPY requirements.txt /src/requirements.txt
RUN pip3 install -r requirements.txt

COPY requirements-dev.txt /src/requirements-dev.txt
RUN pip3 install -r requirements-dev.txt

COPY . /src
RUN pip3 install -e .

ENV NEW_RELIC_APP_NAME "sitesearch"
ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED true
ENV NEW_RELIC_LOG stdout

ENTRYPOINT ["rq", "worker", "--with-scheduler", "-c", "worker_settings"]
