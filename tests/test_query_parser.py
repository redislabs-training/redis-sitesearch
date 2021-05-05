from sitesearch.config import AppConfiguration
from sitesearch.query_parser import parse

config = AppConfiguration()


def test_strips_dash_star_postfixes():
    query = parse("python-*", None, config.default_search_site)
    assert query.query_string() == "python*"


def test_strips_unsafe_chars():
    query = parse("this is a [test]", None, config.default_search_site)
    assert query.query_string() == "this is a  test"


def test_summarizes_body():
    query = parse("test", None, config.default_search_site)
    assert 'body' in query._summarize_fields


def test_highlights_fields():
    query = parse("test", None, config.default_search_site)
    for field in ['title', 'body', 'section_title']:
        assert field in query._highlight_fields


def test_exact_search_for_synonym_terms():
    query = parse("insight*", None, config.default_search_site)
    assert query.query_string() == "insight"


def test_allow_fuzzy_search_for_non_synonym_terms():
    query = parse("test*", None, config.default_search_site)
    assert query.query_string() == "test*"


def test_boosts_current_section_if_given():
    query = parse("test", "test", config.default_search_site)
    assert query.query_string() == "((@s:test) => {$weight: 10} test) | test"
