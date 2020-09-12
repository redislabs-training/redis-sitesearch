import json
import logging
from json import JSONDecodeError

DEFAULT_MAX_LENGTH = 100

log = logging.getLogger(__name__)


def elide_text(text, max_length):
    return text if len(text) < max_length else f"{text[:max_length]}..."


def transform_documents(docs, max_length=DEFAULT_MAX_LENGTH):
    transformed = []

    for doc in docs:
        try:
            hierarchy = json.loads(doc.hierarchy)
        except (JSONDecodeError, ValueError) as e:
            log.error("Bad hierarchy data for doc: %s", doc)
            hierarchy = []

        transformed.append({
            "title": doc.title,
            "section_title": doc.section_title,
            "hierarchy": hierarchy,
            "body": elide_text(doc.body, max_length),
            "url": doc.url
        })

    return transformed
