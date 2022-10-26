import dataclasses
from redisearch.client import TagField, TextField

from sitesearch.models import SiteConfiguration, SynonymGroup
from sitesearch.scorers import boost_pages, boost_top_level_pages
from sitesearch.validators import skip_404_page, skip_release_notes
from sitesearch.sites.redis_labs_landing_pages import LANDING_PAGES
from sitesearch.sites.redis_io_landing_pages import REDIS_IO_LANDING_PAGES


SYNONYMS = [
    SynonymGroup(
        group_id='insight',
        synonyms={'redisinsight', 'insight'}
    ),
    SynonymGroup(
        group_id='active',
        synonyms={'active', 'active active'}
    ),
    SynonymGroup(
        group_id='json',
        synonyms={'json', 'RedisJSON', 'redis json'}
    ),
    SynonymGroup(
        group_id='timeseries',
        synonyms={'timeseries', 'RedisTimeSeries', 'redis timeseries'}
    ),
    SynonymGroup(
        group_id='ai',
        synonyms={'ai', 'RedisAI', 'redis ai'}
    ),
    SynonymGroup(
        group_id='graph',
        synonyms={'graph', 'RedisGraph', 'redis graph'}
    ),
    SynonymGroup(
        group_id='gears',
        synonyms={'gears', 'RedisGears', 'redis gears'}
    ),
    SynonymGroup(
        group_id='search',
        synonyms={'redisearch', 'readisearch', 'search'}
    ),
    SynonymGroup(
        group_id='enterprise',
        synonyms={'enterprise', 'redis enterprise'}
    ),
    SynonymGroup(
        group_id='cloud',
        synonyms={"cloud", "redis enterprise cloud"}
    ),
    SynonymGroup(
        group_id='vss',
        synonyms={"vector", "vector similarity"}
    ),
    SynonymGroup(
        group_id='vs',
        synonyms={"vector", "vector similarity"}
    ),
    # This is to avoid doing a fuzzy search on 'redis' -- the
    # API does exact match searches on synonym terms.
    SynonymGroup(
        group_id='redis',
        synonyms={'redis'}
    )
]

LITERAL_TERMS = (
    'active-active',
    'active-passive',
    'add-on',
    'append-only',
    'as-a-service',
    'auto-scaling',
    'built-in',
    'client-based',
    'conflict-free',
    'crdb-cli',
    'de-provision',
    'geo-distributed',
    'geo-region',
    'high-availability',
    'in-memory',
    'inter-domain',
    'leader-follower',
    'multi-factor',
    'multi-master',
    'multi-tenant',
    'non-blocking',
    'on-premises',
    'open-source',
    'out-of-memory',
    'RAM-based',
    're-sharding',
    'read-only',
    'read-write',
    'redis-cli',
    'role-based',
    'v6.2.8',
    'v6.2.4',
    'v6.0.20',
    'v6.0.12',
    'v6.0.8',
    'v6.0',
    'v5.6.0',
    'v5.4.14',
    'v5.4.10',
    'v5.4.6',
    'v5.4.4',
    'v5.4.2',
    'v5.4',
)

DOCS_PROD = SiteConfiguration(
    url="https://docs.redis.com/latest/",
    synonym_groups=SYNONYMS,
    landing_pages=LANDING_PAGES,
    allowed_domains=('docs.redis.com',),
    search_schema=(
        TextField("title", weight=10),
        TextField("section_title"),
        TextField("body", weight=1.5),
        TextField("url"),
        TextField("s", no_stem=True),
        TagField("doc_id")
    ),
    scorers=(
        boost_pages,
        boost_top_level_pages
    ),
    validators=(
        skip_release_notes,
        skip_404_page
    ),
    deny=(
        r'\/release-notes\/',
        r'.*\.pdf',
        r'\/pdf-gen-.*',
        r'.*\.tgz',
        r'https:\/\/docs\.redis\.com\/latest\/index\.html'
    ),
    allow=(),
    content_classes=(".main-content",),
    literal_terms=LITERAL_TERMS
)

OLD_DOCS_PROD = SiteConfiguration(
    url="https://docs.redislabs.com/latest/",
    synonym_groups=SYNONYMS,
    landing_pages=LANDING_PAGES,
    allowed_domains=('docs.redislabs.com',),
    search_schema=(
        TextField("title", weight=10),
        TextField("section_title"),
        TextField("body", weight=1.5),
        TextField("url"),
        TextField("s", no_stem=True),
        TagField("doc_id")
    ),
    scorers=(
        boost_pages,
        boost_top_level_pages
    ),
    validators=(
        skip_release_notes,
        skip_404_page
    ),
    deny=(
        r'\/release-notes\/',
        r'.*\.tgz',
        r'https:\/\/docs\.redislabs\.com\/latest\/index\.html'
    ),
    allow=(),
    content_classes=(".main-content",),
    literal_terms=LITERAL_TERMS
)

# Uncomment this and replace 'url' with your staging URL to test staging
# branches.
DOCS_STAGING = dataclasses.replace(
    DOCS_PROD,

    url="https://docs.redis.com/staging/boost-current-section"
)

DEVELOPERS = SiteConfiguration(
    url="https://developer.redis.com",
    synonym_groups=SYNONYMS,
    landing_pages={},
    allowed_domains=('developer.redis.com',),
    search_schema=(
        TextField("title", weight=20),
        TextField("section_title"),
        TextField("body", weight=1.5),
        TextField("url"),
        TextField("s", no_stem=True),
    ),
    scorers=(),
    validators=(
        skip_404_page,
    ),
    allow=(),
    deny=(
        r'.*\.pdf',
        r'.*\.tgz',
    ),
    content_classes=(".markdown", ".margin-vert--md", ".main-wrapper"),
    literal_terms=LITERAL_TERMS
)

CORPORATE = SiteConfiguration(
    url="https://redislabs.com",
    synonym_groups=SYNONYMS,
    landing_pages=LANDING_PAGES,
    allowed_domains=('redis.com',),
    search_schema=(
        TextField("title", weight=10),
        TextField("section_title"),
        TextField("body", weight=1.5),
        TextField("url"),
        TextField("s", no_stem=True),
    ),
    scorers=(
        boost_pages,
        boost_top_level_pages
    ),
    validators=(
        skip_404_page,
    ),
    deny=(
        r'.*\.pdf',
        r'.*\.tgz',
        r'\/tag\/.*',
    ),
    allow=(),
    content_classes=(".bounds-content", ".bounds-inner"),
    literal_terms=LITERAL_TERMS
)

OSS = SiteConfiguration(
    url="https://redis.io",
    synonym_groups=SYNONYMS,
    landing_pages=REDIS_IO_LANDING_PAGES,
    allowed_domains=("redis.io",),
    search_schema=(
        TextField("title", weight=15),
        TextField("section_title"),
        TextField("body", weight=1.5),
        TextField("url"),
        TextField("s", no_stem=True),
    ),
    scorers=(
        boost_pages,
    ),
    validators=(
        skip_404_page,
    ),
    deny=(
        r'.*\.pdf',
        r'.*\.tgz',
        r'commands\/.*',
    ),
    allow=(),
    content_classes=(".prose"),
    literal_terms=LITERAL_TERMS
)
