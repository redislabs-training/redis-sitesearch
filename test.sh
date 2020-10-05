#!/bin/bash
redis-server --requirepass $REDIS_PASSWORD --dbfilename dump.rdb --dir /data --save 600 1000 --loadmodule /usr/lib/redis/modules/redisearch.so&
pytest -s
