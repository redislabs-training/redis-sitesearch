from sitesearch.config import AppConfiguration
from sitesearch.query_parser import parse

config = AppConfiguration()


def test_strips_dash_star_postfixes():
    query = parse("index", "python-*", None, 0, 10, config.default_search_site)
    assert query == "FT.SEARCH index python* SUMMARIZE FIELDS 1 body FRAGS 1 LEN 10 HIGHLIGHT FIELDS 3 title body section_title LIMIT 0 10"


def test_strips_unsafe_chars():
    query = parse("index", "this is a [test]", None, 0, 10, config.default_search_site)
    assert query == "FT.SEARCH index this is a  test SUMMARIZE FIELDS 1 body FRAGS 1 LEN 10 HIGHLIGHT FIELDS 3 title body section_title LIMIT 0 10"


def test_summarizes_body():
    query = parse("index", "test", None, 0, 10, config.default_search_site)
    assert "SUMMARIZE FIELDS 1 body" in query


def test_highlights_fields():
    query = parse("index", "test", None, 0, 10, config.default_search_site)
    assert "HIGHLIGHT FIELDS 3 title body section_title" in query


def test_exact_search_for_synonym_terms():
    query = parse("index", "insight*", None, 0, 10, config.default_search_site)
    assert query == "FT.SEARCH index insight SUMMARIZE FIELDS 1 body FRAGS 1 LEN 10 HIGHLIGHT FIELDS 3 title body section_title LIMIT 0 10"


def test_allow_fuzzy_search_for_non_synonym_terms():
    query = parse("index", "test*", None, 0, 10, config.default_search_site)
    assert query == "FT.SEARCH index test* SUMMARIZE FIELDS 1 body FRAGS 1 LEN 10 HIGHLIGHT FIELDS 3 title body section_title LIMIT 0 10"


def test_boosts_current_section_if_given():
    query = parse("index", "test", "test", 0, 10, config.default_search_site)
    assert query == "FT.SEARCH index ((@s:test) => {$weight: 10} test) | test SUMMARIZE FIELDS 1 body FRAGS 1 LEN 10 HIGHLIGHT FIELDS 3 title body section_title LIMIT 0 10"
