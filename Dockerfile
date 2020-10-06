FROM redislabs/redisearch:latest

ARG REDIS_HOST=localhost
ARG PORT=8081

# Install Python 3.8

RUN apt-get update
RUN apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev git supervisor nginx

WORKDIR /
RUN curl -O https://www.python.org/ftp/python/3.8.5/Python-3.8.5.tar.xz && tar -xf Python-3.8.5.tar.xz
WORKDIR Python-3.8.5
RUN ./configure --enable-optimizations
RUN make -j `nproc`
RUN make altinstall

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

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY nginx.conf /etc/nginx/nginx.conf

COPY . /src
RUN pip3 install -e .

# The port on which nginx is listening
EXPOSE 8080/tcp

# The port on which to run the Python app
ENV PORT 8081
ENV NEW_RELIC_APP_NAME "sitesearch"
ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED true
ENV NEW_RELIC_LOG stdout


ENTRYPOINT ["/usr/bin/supervisord"]
