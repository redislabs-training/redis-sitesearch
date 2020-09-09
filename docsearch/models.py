from dataclasses import dataclass


@dataclass(frozen=True)
class SearchDocument:
    doc_id: str
    title: str
    section_title: str
    root_page: str
    parent_page: str
    url: str
    body: str