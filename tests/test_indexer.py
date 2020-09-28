import os
from unittest import mock

from bs4 import BeautifulSoup
import pytest

from docsearch import keys
from docsearch.errors import ParseError
from docsearch.indexer import Indexer, DocumentParser

DOCS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "documents")

FILE_WITH_SECTIONS = "page_with_sections.html"
FILE_WITHOUT_BREADCRUMBS = "page_without_breadcrumbs.html"
FILE_WITHOUT_TITLE = "page_without_title.html"
FILE_WITHOUT_LINK = "page_without_link.html"
FILE_RELEASE_NOTES = "release_notes.html"
FILE_WITH_AN_INDEX = "setup_and_editing.html"

SITE = "http://example.com"


@pytest.fixture()
def indexer():
    mock_search_client = mock.MagicMock()
    yield Indexer(SITE, mock_search_client)


@pytest.fixture()
def parse_file(indexer):
    """
    This fixture parses a file with DocumentParser.

    The fixture is a callable that takes the filename of a document
    and returns the SearchDocuments parsed from the HTML in the file.
    """
    def fn(filename):
        file = os.path.join(DOCS_DIR, filename)
        with open(file, encoding='utf-8') as f:
            html = f.read()

        return DocumentParser().parse(f"{SITE}/test", html)

    return fn


@pytest.fixture()
def index_file(indexer, parse_file):
    """
    This fixture indexes a file using a RediSearch mock -- so that
    we only record the calls made to the client.

    After indexing the document, the fixture turns the Indexer
    object used, so that tests can introspect it.
    """
    def fn(filename):
        for doc in parse_file(filename):
            indexer.index_document(doc)
        return indexer

    return fn


def test_indexer_indexes_page_document(index_file):
    indexer = index_file(FILE_WITH_SECTIONS)
    page_url = f"{SITE}/test"
    expected_doc = {
        'doc_id': f'{page_url}:Database Persistence with Redis Enterprise Software',
        'title': 'Database Persistence with Redis Enterprise Software',
        'section_title': '',
        'hierarchy': '["Redis Enterprise Software", "Concepts and Architecture", "Data Access Architecture", "Database Persistence with Redis Enterprise Software"]',
        'url': page_url,
        'body': 'All data is stored and managed exclusively in either RAM or RAM + Flash Memory (Redis on Flash) and therefore, is at risk of being lost upon a\xa0process or server failure.\xa0As Redis Enterprise Software is not just a caching solution, but also a full-fledged database, persistence to disk is critical. Therefore, Redis Enterprise Software supports persisting data to disk on a per-database basis and in multiple ways. There are two options for persistence:  Append Only File (AOF) - A continuous writing of data to disk Snapshot (RDB) - An automatic periodic snapshot writing to disk  Data persistence, via either mechanism, is used solely to rehydrate the database if the database process fails for any reason. It is not a replacement for backups, but something you do in addition to backups. To disable data persistence, select None. AOF writes the latest ‘write’ commands into a file every second, it resembles a traditional RDBMS’s redo log, if you are familiar with that. This file can later be ‘replayed’ in order to recover from a crash. A snapshot (RDB) on the other hand, is performed every one, six, or twelve hours. The snapshot is a dump of the data and while there is a potential of losing up to one hour of data, it is dramatically faster to recover from a snapshot compared to AOF recovery. Persistence can be configured either at time of database creation or by editing an existing database’s configuration. While the persistence model can be changed dynamically, just know that it can take time for your database to switch from one persistence model to the other. It depends on what you are switching from and to, but also on the size of your database. Note: For performance reasons, if you are going to be using AOF, it is highly recommended to make sure replication is enabled for that database as well. When these two features are enabled, persistence is performed\xa0on the database slave and does not impact performance on the master. Options for configuring data persistence There are six\xa0options for persistence in Redis Enterprise Software:    Options Description     None Data is not persisted to disk at all.   Append Only File (AoF) on every write Data is fsynced to disk with every write.   Append Only File (AoF) one second Data is fsynced to disk every second.   Snapshot every 1 hour A snapshot of the database is created every hour.   Snapshot every 6 hours A snapshot of the database is created every 6 hours.   Snapshot every 12 hours A snapshot of the database is created every 12 hours.    The first thing you need to do is determine if you even need persistence. Persistence is used to recover from a catastrophic failure, so make sure that you need to incur the overhead of persistence before you select it. If the database is being used as a cache, then you may not need persistence. If you do need persistence, then you need to identify\xa0which is the best type for your use case. Append only file (AOF) vs snapshot (RDB) Now that you know the available options, to assist in making a decision on which option is right for your use case, here is a table about the two:    Append Only File (AOF) Snapshot (RDB)     More resource intensive Less resource\xa0intensive   Provides better durability (recover the latest point in time) Less durable   Slower time to recover (Larger files) Faster recovery time   More disk space required (files tend to grow large and require compaction) Requires less resource (I/O once every several hours and no compaction required)    Data persistence and Redis on Flash If you are enabling data persistence for databases running on Redis Enterprise Flash, by default both master and slave shards are configured to write to disk. This is unlike a standard Redis Enterprise Software database where only the slave shards persist to disk. This master and slave dual data persistence with replication is done to better protect the database against node failures. Flash-based databases are expected to hold larger datasets and repair times for shards can be longer under node failures. Having dual-persistence provides better protection against failures under these longer repair times. However, the dual data persistence with replication adds some processor and network overhead, especially in the case of cloud configurations with persistent storage that is network attached (e.g. EBS-backed volumes in AWS). There may be times where performance is critical for your use case and you don’t want to risk data persistence adding latency. If that is the case, you can disable data-persistence on the master shards using the following\xa0rladmin command: rladmin tune db db: master_persistence disabled     Page Contents   Options for configuring data persistence   Append only file (AOF) vs snapshot (RDB)   Data persistence and Redis on Flash',
        'type': 'page',
        'position': 0,
        'score': 0.6989700043360187
    }
    key = keys.document('http://example.com', expected_doc['doc_id'])
    indexer.search_client.redis.hset.assert_any_call(key, mapping=expected_doc)


def test_indexer_indexes_page_section_documents(index_file):
    indexer = index_file(FILE_WITH_SECTIONS)
    page_url = f"{SITE}/test"
    expected_section_docs = [
        {
            'doc_id': f'{page_url}:Database Persistence with Redis Enterprise Software:Options for configuring data persistence:0',
            'title': 'Database Persistence with Redis Enterprise Software',
            'section_title': 'Options for configuring data persistence',
            'hierarchy': '["Redis Enterprise Software", "Concepts and Architecture", "Data Access Architecture", "Database Persistence with Redis Enterprise Software"]',
            'url': page_url,
            'body': 'There are six\xa0options for persistence in Redis Enterprise Software:    Options Description     None Data is not persisted to disk at all.   Append Only File (AoF) on every write Data is fsynced to disk with every write.   Append Only File (AoF) one second Data is fsynced to disk every second.   Snapshot every 1 hour A snapshot of the database is created every hour.   Snapshot every 6 hours A snapshot of the database is created every 6 hours.   Snapshot every 12 hours A snapshot of the database is created every 12 hours.    The first thing you need to do is determine if you even need persistence. Persistence is used to recover from a catastrophic failure, so make sure that you need to incur the overhead of persistence before you select it. If the database is being used as a cache, then you may not need persistence. If you do need persistence, then you need to identify\xa0which is the best type for your use case.',
            'type': 'section',
            'position': 0,
            'score': 0.1989700043360188,
        },
        {
            'doc_id': f'{page_url}:Database Persistence with Redis Enterprise Software:Append only file (AOF) vs snapshot (RDB):1',
            'title': 'Database Persistence with Redis Enterprise Software',
            'section_title': 'Append only file (AOF) vs snapshot (RDB)',
            'hierarchy': '["Redis Enterprise Software", "Concepts and Architecture", "Data Access Architecture", "Database Persistence with Redis Enterprise Software"]',
            'url': page_url,
            'body': 'Now that you know the available options, to assist in making a decision on which option is right for your use case, here is a table about the two:    Append Only File (AOF) Snapshot (RDB)     More resource intensive Less resource\xa0intensive   Provides better durability (recover the latest point in time) Less durable   Slower time to recover (Larger files) Faster recovery time   More disk space required (files tend to grow large and require compaction) Requires less resource (I/O once every several hours and no compaction required)',
            'type': 'section',
            'position': 1,
            'score': 0.1989700043360188,
        },
        {
            'doc_id': f'{SITE}/test:Database Persistence with Redis Enterprise Software:Data persistence and Redis on Flash:2',
            'title': 'Database Persistence with Redis Enterprise Software',
            'section_title': 'Data persistence and Redis on Flash',
            'hierarchy': '["Redis Enterprise Software", "Concepts and Architecture", "Data Access Architecture", "Database Persistence with Redis Enterprise Software"]',
            'url': page_url,
            'body': 'If you are enabling data persistence for databases running on Redis Enterprise Flash, by default both master and slave shards are configured to write to disk. This is unlike a standard Redis Enterprise Software database where only the slave shards persist to disk. This master and slave dual data persistence with replication is done to better protect the database against node failures. Flash-based databases are expected to hold larger datasets and repair times for shards can be longer under node failures. Having dual-persistence provides better protection against failures under these longer repair times. However, the dual data persistence with replication adds some processor and network overhead, especially in the case of cloud configurations with persistent storage that is network attached (e.g. EBS-backed volumes in AWS). There may be times where performance is critical for your use case and you don’t want to risk data persistence adding latency. If that is the case, you can disable data-persistence on the master shards using the following\xa0rladmin command: rladmin tune db db: master_persistence disabled',
            'type': 'section',
            'position': 2,
            'score': 0.1989700043360188
        }
    ]

    for doc in expected_section_docs:
        key = keys.document('http://example.com', doc['doc_id'])
        indexer.search_client.redis.hset.assert_any_call(key, mapping=doc)


def test_document_parser_skips_pages_without_breadcrumbs(parse_file):
    with pytest.raises(ParseError):
        parse_file(FILE_WITHOUT_BREADCRUMBS)


def test_document_parser_skips_pages_without_title(parse_file):
    with pytest.raises(ParseError):
        parse_file(FILE_WITHOUT_TITLE)


def test_document_parser_skips_release_notes(parse_file):
    with pytest.raises(ParseError):
        parse_file(FILE_RELEASE_NOTES)


def test_document_parser_extracts_one_page():
    html = BeautifulSoup("""
    <div id="breadcrumbs" itemscope="" itemtype="http://data-vocabulary.org/Breadcrumb">
          <span class="links">
            <a href="../" class="highlight">Redis Labs Documentation</a> <span>&gt;</span> Platforms
          </span>
        </div>
    """, 'html.parser')
    assert DocumentParser().extract_hierarchy(html) == ["Platforms"]


def test_document_parser_extracts_multiple_pages():
    html = BeautifulSoup("""
        <div id="breadcrumbs" itemscope="" itemtype="http://data-vocabulary.org/Breadcrumb">
          <span class="links">
            <a href="../../" class="highlight">Redis Labs Documentation</a> <span>&gt;</span> <a href="../../rc/" class="highlight">Redis Enterprise Cloud</a> <span>&gt;</span> How Tos
          </span>
        </div>
    """, 'html.parser')
    assert DocumentParser().extract_hierarchy(html) == ["Redis Enterprise Cloud", "How Tos"]


def test_parsing_page_with_links_in_h2s_returns_body_content(parse_file):
    """A regression test."""
    docs = parse_file(FILE_WITH_AN_INDEX)
    for doc in docs:
        assert doc.body is not None
