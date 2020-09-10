from dataclasses import dataclass
from typing import List


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