import pytest

from sitesearch import validators
from sitesearch.errors import ParseError
from sitesearch.models import SearchDocument, TYPE_PAGE


def test_skip_release_notes_passes_non_release_notes():
    doc = SearchDocument(
        doc_id="123",
        title="Title",
        section_title="Section",
        hierarchy=["one", "two"],
        s="",
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
        hierarchy=["one", "two"],
        s="",
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    with pytest.raises(ParseError):
        assert validators.skip_release_notes(doc)


def test_skip_404_skips_404_hierarchy():
    doc = SearchDocument(
        doc_id="123",
        title="Title",
        section_title="Section",
        hierarchy=["404 Page not found"],
        s="",
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    with pytest.raises(ParseError):
        assert validators.skip_404_page(doc)


def test_skip_404_skips_404_url():
    doc = SearchDocument(
        doc_id="123",
        title="Title",
        section_title="Section",
        hierarchy=["404 Page not found"],
        s="",
        url="https://docs.redislabs.com/latest/404.html",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    with pytest.raises(ParseError):
        assert validators.skip_404_page(doc)


def test_skip_404_allows_non_404():
    doc = SearchDocument(
        doc_id="123",
        title="Title",
        section_title="Section",
        hierarchy=["Some really cool page"],
        s="",
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    assert validators.skip_404_page(doc) is None
