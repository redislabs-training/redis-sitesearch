FROM redislabs/redisearch:latest

ARG REDIS_PASSWORD=password
ARG REDIS_HOST=localhost
ARG PORT=8081
ARG API_KEY=key

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

# Hack to avoid docker reinstalling every build
COPY requirements.txt /src/requirements.txt
COPY constraints.txt /src/constraints.txt

WORKDIR /src
RUN pip3 install -r requirements.txt -c constraints.txt

COPY . /src
RUN pip3 install .

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080/tcp

ENV REDIS_PASSWORD ${REDIS_PASSWORD}
ENV REDIS_HOST ${REDIS_HOST}
ENV PORT ${PORT}
ENV API_KEY ${API_KEY}

ENTRYPOINT ["/usr/bin/supervisord"]
