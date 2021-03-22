FROM python:3.8

# ---------------
# Install the app
# ---------------

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.8 get-pip.py
RUN pip3 install --upgrade pip

WORKDIR /redis-sitesearch

# Hack to avoid docker reinstalling every build
COPY requirements.txt /redis-sitesearch/requirements.txt
RUN pip3 install -r /redis-sitesearch/requirements.txt

COPY requirements-dev.txt /redis-sitesearch/requirements-dev.txt
RUN pip3 install -r /redis-sitesearch/requirements-dev.txt

COPY . /redis-sitesearch
RUN pip3 install -e /redis-sitesearch

ENV NEW_RELIC_APP_NAME "sitesearch"
ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED true
ENV NEW_RELIC_LOG stdout

ENTRYPOINT ["scheduler"]
