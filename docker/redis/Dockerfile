FROM redislabs/redisearch:latest

CMD redis-server --requirepass $REDIS_PASSWORD --appendonly yes --aof-use-rdb-preamble yes --dir /data --loadmodule /usr/lib/redis/modules/redisearch.so MINPREFIX 1
