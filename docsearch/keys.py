import os

DEFAULT_PREFIX = "docsearch:test"

PREFIX = os.environ.get('KEY_PREFIX', DEFAULT_PREFIX)


def document(url: str, doc_id: str):
    return f"{PREFIX}:doc:{url}:{doc_id}"


def last_index(url: str):
    return f"{PREFIX}:{url}:last_indexing_time"


def index_name(url: str):
    return f"{PREFIX}:{url}"
