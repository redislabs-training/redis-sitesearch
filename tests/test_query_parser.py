from docsearch.models import SynonymGroup
from docsearch.query_parser import parse


def test_strips_dash_star_postfixes():
    query = parse("python-*")
    assert query.query_string() == "python*"


def test_strips_unsafe_chars():
    query = parse("this is a [test] of @tag and subtraction- chars+")
    assert query.query_string() == "this is a  test  of  tag and subtraction  chars"


def test_summarizes_body():
    query = parse("test")
    assert 'body' in query._summarize_fields


def test_highlights_fields():
    query = parse("test")
    for field in ['title', 'body', 'section_title']:
        assert field in query._highlight_fields


def test_exact_search_for_synonym_terms():
    query = parse("test*", synonyms=[SynonymGroup(group_id="test", synonyms={"test"})])
    assert query.query_string() == "test"


def test_exact_search_for_synonym_terms():
    query = parse("test*", synonyms=[SynonymGroup(group_id="test", synonyms={"test"})])
    assert query.query_string() == "test"


def test_allow_fuzzy_search_for_non_synonym_terms():
    query = parse("test*")
    assert query.query_string() == "test*"
