from sitesearch.config import Config
from sitesearch.query_parser import parse

config = Config()


def test_strips_dash_star_postfixes():
    query = parse("python-*", config.default_search_site)
    assert query.query_string() == "python*"


def test_strips_unsafe_chars():
    query = parse("this is a [test] of @tag and subtraction- chars+",
                  config.default_search_site)
    assert query.query_string() == "this is a  test  of  tag and subtraction  chars"


def test_summarizes_body():
    query = parse("test", config.default_search_site)
    assert 'body' in query._summarize_fields


def test_highlights_fields():
    query = parse("test", config.default_search_site)
    for field in ['title', 'body', 'section_title']:
        assert field in query._highlight_fields


def test_exact_search_for_synonym_terms():
    query = parse("insight*", config.default_search_site)
    assert query.query_string() == "insight"


def test_allow_fuzzy_search_for_non_synonym_terms():
    query = parse("test*", config.default_search_site)
    assert query.query_string() == "test*"
