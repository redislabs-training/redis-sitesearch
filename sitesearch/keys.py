import os

DEFAULT_PREFIX = "sitesearch:test"

PREFIX = os.environ.get('KEY_PREFIX', DEFAULT_PREFIX)


def document(url: str, doc_id: str):
    return f"{PREFIX}:{url}:doc:{doc_id}"


def last_index(url: str):
    return f"{PREFIX}:{url}:last_indexing_time"


def index_name(url: str):
    return f"{PREFIX}:{url}"


def startup_indexing_job_ids():
    return f"{PREFIX}:startup_indexing_tasks"


def site_indexes(index_name: str):
    return f"{PREFIX}:{index_name}:indexes"
