FROM python:3.8

RUN apt-get clean
RUN apt-get update
RUN apt-get install -o Acquire::ForceIPv4=true -y supervisor nginx

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

COPY docker/app/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY nginx.conf /etc/nginx/nginx.conf

COPY . /redis-sitesearch
RUN pip3 install -e /redis-sitesearch

# The port on which nginx is listening
EXPOSE 8080/tcp

# The port on which to run the Python app
ENV PORT 8081
ENV NEW_RELIC_APP_NAME "sitesearch"
ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED true
ENV NEW_RELIC_LOG stdout

ENTRYPOINT ["/usr/bin/supervisord"]
