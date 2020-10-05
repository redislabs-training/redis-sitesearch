import dataclasses
from redisearch.client import TextField

from docsearch.models import SearchDocument, SiteConfiguration, SynonymGroup, TYPE_PAGE
from docsearch.scorers import boost_pages, boost_top_level_pages
from docsearch.validators import skip_404_page, skip_release_notes


SYNONYMS = [
    SynonymGroup(
        group_id='insight',
        synonyms={'redisinsight', 'insight'}
    ),
    SynonymGroup(
        group_id='active',
        synonyms={'active', 'active-active', 'active active'}
    ),
    SynonymGroup(
        group_id='json',
        synonyms={'json', 'RedisJSON', 'redis json'}
    ),
    SynonymGroup(
        group_id='timeseries',
        synonyms={'timeseries', 'RedisTimeries', 'redis timeseries'}
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
    # This is to avoid doing a fuzzy search on 'redis' -- the
    # API does exact match searches on synonym terms.
    SynonymGroup(
        group_id='redis',
        synonyms={'redis'}
    )
]

CLOUD_LANDING_PAGE = SearchDocument(
    doc_id="redislabs://docs/landing/cloud",  # Note: this is a fake document ID,
    title="Redis Enterprise Cloud",
    section_title="",
    hierarchy=["Redis Enterprise Cloud"],
    url="latest/rc/",
    body="Redis Enterprise <b>Cloud</b> delivers a cost-effective, fully "
            "managed Database-as-a-Service (DBaaS) offering, fully hosted on public clouds.",
    type=TYPE_PAGE,
    position=0
)

LANDING_PAGES = {
    'cloud': CLOUD_LANDING_PAGE,
    'redis cloud': CLOUD_LANDING_PAGE,
    'redis enterprise cloud': CLOUD_LANDING_PAGE,
}

DOCS_PROD = SiteConfiguration(
    url="https://docs.redislabs.com/",
    synonym_groups=SYNONYMS,
    landing_pages=LANDING_PAGES,
    schema=(
        TextField("title", weight=10),
        TextField("section_title"),
        TextField("body", weight=1.5),
        TextField("url"),
    ),
    scorers=(
        boost_pages,
        boost_top_level_pages
    ),
    validators=(
        skip_release_notes,
        skip_404_page
    )
)

DOCS_STAGING = dataclasses.replace(
    DOCS_PROD,
    url="https://docs.redislabs.com/staging/docs-with-RediSearch"
)
