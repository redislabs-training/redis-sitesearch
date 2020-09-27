from docsearch.errors import ParseError
from docsearch.models import SearchDocument


def skip_release_notes(doc: SearchDocument):
    if 'Release Notes' in doc.title:
        raise ParseError("Skipping release notes")


def skip_404_page(doc: SearchDocument):
    if '404 Page not found' in doc.hierarchy:
        raise ParseError("Skipping 404 page")