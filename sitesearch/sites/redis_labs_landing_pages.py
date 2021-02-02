from sitesearch.models import SearchDocument, TYPE_PAGE


CLOUD_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/cloud",  # Note: this is a fake document ID,
    title="Redis Enterprise Cloud",
    section_title="",
    hierarchy=["Redis Enterprise Cloud"],
    s="rc",
    url="latest/rc/",
    body="Redis Enterprise <b>Cloud</b> delivers a cost-effective, fully "
            "managed Database-as-a-Service (DBaaS) offering, fully hosted on public clouds.",
    type=TYPE_PAGE,
    position=0
)

SOFTWARE_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/software",  # Note: this is a fake document ID,
    title="Redis Enterprise Software",
    section_title="",
    hierarchy=["Redis Enterprise Software"],
    s="rs",
    url="latest/rs/",
    body="Redis Enterprise is a robust, in-memory database platform built by the same people "
         "who develop open-source Redis.",
    type=TYPE_PAGE,
    position=0
)

ACTIVE_ACTIVE_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/active-active",  # Note: this is a fake document ID,
    title="Geo-Distributed <b>Active</b>-Active Redis Applications",
    section_title="",
    hierarchy=["Redis Enterprise Software", "Concepts and Architecture", "Geo-Distributed Active-Active Redis Applications"],
    s="rs",
    url="latest/rs/concepts/intercluster-replication/",
    body="Developing globally distributed applications can be challenging, as developers "
         "have to think about race conditions and complex combinations of events under "
         "geo-failovers and cross-region write conflicts.",
    type=TYPE_PAGE,
    position=0
)

FLASH_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/flash",  # Note: this is a fake document ID,
    title="Redis on Flash",
    section_title="",
    hierarchy=["Redis Enterprise Software", "Concepts and Architecture",
               "Memory Architecture in Redis Enterprise Software", "Redis on Flash"],
    s="rs",
    url="latest/rs/concepts/memory-architecture/redis-flash/",
    body="Redis on Flash (RoF) offers users of Redis Enterprise Software and "
         "Redis Enterprise Cloud the unique ability to have very large Redis "
         "databases but at significant cost savings.",
    type=TYPE_PAGE,
    position=0
)

REDIS_INSIGHT_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/redisinsight",  # Note: this is a fake document ID,
    title="RedisInsight",
    section_title="",
    hierarchy=["RedisInsight"],
    s="ri",
    url="latest/ri/",
    body="Information on how to install and use RedisInsight, a GUI for administering Redis.",
    type=TYPE_PAGE,
    position=0
)

GEARS_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/redisgears",  # Note: this is a fake document ID,
    title="RedisGears",
    section_title="",
    hierarchy=["Redis Modules", "RedisGears"],
    s="modules",
    url="latest/modules/redisgears/",
    body="RedisGears is an engine for data processing in Redis. RedisGears "
         "supports batch and event-driven processing for Redis data.",
    type=TYPE_PAGE,
    position=0
)

SEARCH_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/redisearch",  # Note: this is a fake document ID,
    title="RediSearch",
    section_title="",
    hierarchy=["Redis Modules", "RediSearch"],
    s="modules",
    url="latest/modules/redisearch/",
    body="The RediSearch 2.x module is a source-available project that lets you build "
         "powerful searches for open-source Redis databases.",
    type=TYPE_PAGE,
    position=0
)

GRAPH_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/redisgraph",  # Note: this is a fake document ID,
    title="RedisGraph",
    section_title="",
    hierarchy=["Redis Modules", "RedisGraph"],
    s="modules",
    url="latest/modules/redisgraph/",
    body="RedisGraph is the first queryable Property Graph database to use sparse matrices "
         "to represent the adjacency matrix in graphs and linear algebra to query the graph.",
    type=TYPE_PAGE,
    position=0
)

JSON_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/redisjson",  # Note: this is a fake document ID,
    title="RedisJSON",
    section_title="",
    hierarchy=["Redis Modules", "RedisJSON"],
    s="modules",
    url="latest/modules/redisjson/",
    body="Applications developed with the open source version of RedisJSON are 100% "
         "compatible with RedisJSON in Redis Enterprise Software (RS).",
    type=TYPE_PAGE,
    position=0
)

TIMESERIES_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/redistimeseries",  # Note: this is a fake document ID,
    title="RedisTimeSeries",
    section_title="",
    hierarchy=["Redis Modules", "RedisTimeSeries"],
    s="modules",
    url="latest/modules/redistimeseries/",
    body="RedisTimeSeries is a Redis module developed by Redis Labs to enhance your "
         "experience managing time series data with Redis.",
    type=TYPE_PAGE,
    position=0
)

BLOOM_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/redisbloom",  # Note: this is a fake document ID,
    title="RedisBloom",
    section_title="",
    hierarchy=["Redis Modules", "RedisBloom"],
    s="modules",
    url="latest/modules/redisbloom/",
    body="A Bloom filter is a probabilistic data structure which provides an efficient "
         "way to verify that an entry is certainly not in a set.",
    type=TYPE_PAGE,
    position=0
)

AI_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/redisai",  # Note: this is a fake document ID,
    title="RedisAI",
    section_title="",
    hierarchy=["Redis Modules", "RedisAI"],
    s="modules",
    url="latest/modules/redisai/",
    body="RedisAI is a Redis module for executing Deep Learning/Machine Learning models "
         "and managing their data. ",
    type=TYPE_PAGE,
    position=0
)

MODULES_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/modules",  # Note: this is a fake document ID,
    title="Redis Modules",
    section_title="",
    hierarchy=["Redis Modules"],
    s="modules",
    url="latest/modules/",
    body="Redis Labs develops and packages modules for redis. The modules listed here "
         "are supported with Redis Enterprise Software (RS) clusters and Redis Cloud Pro (RC Pro).",
    type=TYPE_PAGE,
    position=0
)

K8S_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/k8s",  # Note: this is a fake document ID,
    title="Getting Started with Redis Enterprise Software using Kubernetes",
    section_title="",
    hierarchy=["Platforms", "Getting Started with Redis Enterprise Software using Kubernetes"],
    url="latest/platforms/kubernetes/",
    s="platforms",
    body="Getting a Redis Enterprise cluster running on Kubernetes is simple with the Redis Enterprise Operator.",
    type=TYPE_PAGE,
    position=0
)



LANDING_PAGES = {
    'cloud': CLOUD_LANDING_PAGE,
    'redis cloud': CLOUD_LANDING_PAGE,
    'redis enterprise cloud': CLOUD_LANDING_PAGE,
    'rc': CLOUD_LANDING_PAGE,

    'software': SOFTWARE_LANDING_PAGE,
    'rs': SOFTWARE_LANDING_PAGE,

    'active': ACTIVE_ACTIVE_LANDING_PAGE,
    'active-active': ACTIVE_ACTIVE_LANDING_PAGE,

    'rof': FLASH_LANDING_PAGE,

    'gui': REDIS_INSIGHT_LANDING_PAGE,
    'insi': REDIS_INSIGHT_LANDING_PAGE,
    'insigh': REDIS_INSIGHT_LANDING_PAGE,
    'insight': REDIS_INSIGHT_LANDING_PAGE,

    'gears': GEARS_LANDING_PAGE,

    'search': SEARCH_LANDING_PAGE,

    'graph': GRAPH_LANDING_PAGE,

    'json': JSON_LANDING_PAGE,
    'redisjson': JSON_LANDING_PAGE,

    'time': TIMESERIES_LANDING_PAGE,
    'times': TIMESERIES_LANDING_PAGE,
    'timese': TIMESERIES_LANDING_PAGE,
    'timeserie': TIMESERIES_LANDING_PAGE,
    'timeseries': TIMESERIES_LANDING_PAGE,

    'bloom': BLOOM_LANDING_PAGE,

    'ai': AI_LANDING_PAGE,
    'ml': AI_LANDING_PAGE,

    'modules': MODULES_LANDING_PAGE,

    'k8': K8S_LANDING_PAGE,
    'k8s': K8S_LANDING_PAGE,
    'kubernetes': K8S_LANDING_PAGE
}
