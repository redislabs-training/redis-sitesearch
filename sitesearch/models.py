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
    position: int = 0


@dataclass(frozen=True)
class SynonymGroup:
    group_id: str
    synonyms: Set[str]


ScoreFn = Callable[[SearchDocument, float], float]
ValidatorFn = Callable[[SearchDocument], None]


@dataclass(frozen=True)
class SiteConfiguration:
    url: str
    synonym_groups: List[SynonymGroup]
    schema: Tuple[Field]
    scorers: Tuple[ScoreFn]
    validators: Tuple[ValidatorFn]
    landing_pages: Dict[str, SearchDocument]
    allow: Tuple[Pattern]
    deny: Tuple[Pattern]

    @property
    def all_synonyms(self) -> Set[str]:
        synonyms = set()
        for syn_group in self.synonym_groups:
            synonyms |= syn_group.synonyms
        return synonyms

    @property
    def index_name(self) -> str:
        return keys.index_name(self.url)

    def landing_page(self, query) -> SearchDocument:
        page = self.landing_pages.get(query, None)
        separator = "" if self.url.endswith("/") else "/"
        if page:
            page = replace(page, url=f"{self.url}{separator}{page.url}")
        return page
