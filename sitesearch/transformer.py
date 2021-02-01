import json
import logging
from json import JSONDecodeError
from typing import List, Dict, Any

from sitesearch.models import SiteConfiguration


DEFAULT_MAX_LENGTH = 100

log = logging.getLogger(__name__)


def elide_text(text, max_length):
    return text if len(text) < max_length else f"{text[:max_length]}..."


def transform_documents(docs: List[Any],
                        search_site: SiteConfiguration,
                        query: str,
                        max_length=DEFAULT_MAX_LENGTH) -> List[Dict[str, str]]:
    """
    Transform a list of Documents from RediSearch into a list of dictionaries.
    """
    transformed = []
    landing_page = search_site.landing_page(query.replace('*', ''))
    pages_seen = set()

    if landing_page:
        transformed.append({
            "title": landing_page.title,
            "section_title": landing_page.section_title,
            "hierarchy": landing_page.hierarchy,
            "body": elide_text(landing_page.body, max_length),
            "url": landing_page.url
        })
        pages_seen.add((*landing_page.hierarchy, landing_page.title))

    for doc in docs:
        try:
            hierarchy = json.loads(doc.hierarchy)
        except (JSONDecodeError, ValueError):
            log.error("Bad hierarchy data for doc: %s", doc)
            hierarchy = []

        # Only include one result per page
        if (*hierarchy, doc.title) in pages_seen:
            continue

        transformed.append({
            "title": doc.title,
            "section_title": doc.section_title,
            "hierarchy": hierarchy,
            "body": elide_text(doc.body, max_length),
            "url": doc.url
        })

        pages_seen.add((*hierarchy, doc.title))

    return transformed
