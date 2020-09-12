import pytest

from docsearch import validators
from docsearch.errors import ParseError
from docsearch.models import SearchDocument, TYPE_PAGE


def test_skip_release_notes_passes_non_release_notes():
    doc = SearchDocument(
        doc_id="123",
        title="Title",
        section_title="Section",
        hierarchy='["one","two"]',
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    assert validators.skip_release_notes(doc) is None


def test_skip_release_notes_skips_release_notes():
    doc = SearchDocument(
        doc_id="123",
        title="RediSearch Release Notes 2020",
        section_title="Section",
        hierarchy='["one","two"]',
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    with pytest.raises(ParseError):
        assert validators.skip_release_notes(doc)