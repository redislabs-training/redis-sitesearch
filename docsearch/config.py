import os

from redisearch.client import TextField

from docsearch.models import SiteConfiguration, SynonymGroup
from docsearch.scorers import boost_pages, boost_top_level_pages
from docsearch.validators import skip_release_notes


REDIS_LABS_SYNONYMS = [
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
        group_id='enterprise',
        synonyms={'enterprise', 'redis enterprise'}
    )
]

REDIS_LABS_SCHEMA = (
    TextField("title", weight=10),
    TextField("section_title", weight=1.2),
    TextField("body"),
    TextField("url"),
)

REDIS_LABS_VALIDATORS = (
    skip_release_notes,
)

REDIS_LABS_SCORERS = (
    boost_pages,
    boost_top_level_pages
)

REDIS_LABS_DOCS_PROD = SiteConfiguration(
    url="https://docs.redislabs.com/",
    synonym_groups=REDIS_LABS_SYNONYMS,
    schema=REDIS_LABS_SCHEMA,
    scorers=REDIS_LABS_SCORERS,
    validators=REDIS_LABS_VALIDATORS
)

REDIS_LABS_DOCS_STAGING = SiteConfiguration(
    url="https://docs.redislabs.com/staging/docs-with-RediSearch",
    synonym_groups=REDIS_LABS_SYNONYMS,
    schema=REDIS_LABS_SCHEMA,
    scorers=REDIS_LABS_SCORERS,
    validators=REDIS_LABS_VALIDATORS
)


class Config:
    def __init__(self):
        if os.environ.get('ENV') == 'development':
            self.sites = [REDIS_LABS_DOCS_STAGING]
            self.default_search_site = REDIS_LABS_DOCS_STAGING
            return

        self.sites = [REDIS_LABS_DOCS_PROD]
        self.default_search_site = REDIS_LABS_DOCS_PROD
