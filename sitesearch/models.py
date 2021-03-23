from dataclasses import InitVar, dataclass, field, replace
from typing import Dict, List, Set, Tuple, Callable, Pattern

from sitesearch import keys
from redisearch.client import Field

TYPE_PAGE = "page"
TYPE_SECTION = "section"


@dataclass(frozen=True)
class SearchDocument:
    doc_id: str
    title: str
    section_title: str
    hierarchy: List[str]
    url: str
    body: str
    type: str
    s: str  # Shortcut for the root page or "section" of the URL.
    position: int = 0


@dataclass(frozen=True)
class SynonymGroup:
    group_id: str
    synonyms: Set[str]


Scorer = Callable[[SearchDocument, float], float]
Validator = Callable[[SearchDocument], None]


@dataclass(frozen=True)
class SiteConfiguration:
    url: str
    schema: Tuple[Field]
    synonym_groups: List[SynonymGroup]
    scorers: Tuple[Scorer]
    validators: Tuple[Validator]
    landing_pages: Dict[str, SearchDocument]
    allow: Tuple[Pattern]
    deny: Tuple[Pattern]
    allowed_domains: Tuple[str]
    content_classes: Tuple[str] = None

    @property
    def all_synonyms(self) -> Set[str]:
        synonyms = set()
        for syn_group in self.synonym_groups:
            synonyms |= syn_group.synonyms
        return synonyms

    def landing_page(self, query) -> SearchDocument:
        page = self.landing_pages.get(query, None)
        if page:
            root_url = self.url.rstrip('/')
            page_url = page.url.lstrip('/')
            page = replace(page, url=f"{root_url}/{page_url}")
        return page
