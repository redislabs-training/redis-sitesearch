import os
from unittest import mock
from unittest.mock import call

import pytest

from sitesearch.keys import Keys
from sitesearch.config import DOCS_PROD
from sitesearch.errors import ParseError
from sitesearch.indexer import DocumentParser, Indexer
from sitesearch.models import SearchDocument

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "documents")

FILE_WITH_SECTIONS = "page_with_sections.html"
FILE_WITHOUT_BREADCRUMBS = "page_without_breadcrumbs.html"
FILE_WITHOUT_TITLE = "page_without_title.html"
FILE_WITHOUT_LINK = "page_without_link.html"
FILE_RELEASE_NOTES = "release_notes.html"
FILE_WITH_AN_INDEX = "setup_and_editing.html"
FILE_WITH_H3s = "file_with_h3s.html"

TEST_URL = f"{DOCS_PROD.url}/test"


@pytest.fixture()
def indexer(app_config):
    mock_search_client = mock.MagicMock()
    yield Indexer(DOCS_PROD, app_config, mock_search_client)


@pytest.fixture()
def keys(app_config):
    yield Keys(prefix=app_config.key_prefix)


@pytest.fixture()
def parse_file():
    """
    This fixture parses a file with DocumentParser.

    The fixture is a callable that takes the filename of a document
    and returns the SearchDocuments parsed from the HTML in the file.
    """
    def fn(filename):
        file = os.path.join(DOCS_DIR, filename)
        with open(file, encoding='utf-8') as f:
            html = f.read()

        return DocumentParser(DOCS_PROD).parse(TEST_URL, html)

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


def test_indexer_indexes_page_document(index_file, keys):
    """Test indexing pages.
    
    NOTE: If this test fails, it may be that you changed the fixture HTML.
    Changing the HTML may cause the test to fail because the MD5 hash of
    the HTML will change, thus the "doc_id" will be different. If this happens,
    you can find the new hash by adding `import ipdb; ipdb.set_trace()` into
    this test and running the tests with the `-s` flag. Then check the value
    of the mock calls, e.g.:
    
        ipdb> indexer.search_client.redis.hset.call_args_list[3]
        call('<key>', mapping={'doc_id': 'https://docs.redislabs.com/latest//test:page:c63108b05d076d2cdff93c6065bf362e', ... )
    """ 
    indexer = index_file(FILE_WITH_SECTIONS)
    expected_doc = {
        'doc_id': f'{TEST_URL}:page:c34e3cb81555c9fa4346342034476dd7',
        'title': 'Database Persistence with Redis Enterprise Software',
        'section_title': '',
        'hierarchy': '[]',
        'url': TEST_URL,
        's': 'test',
        'body':
        'All data is stored and managed exclusively in either RAM or RAM + Flash Memory (Redis on Flash) and therefore, is at risk of being lost upon a\xa0process or server failure.\xa0As Redis Enterprise Software is not just a caching solution, but also a full-fledged database, persistence to disk is critical. Therefore, Redis Enterprise Software supports persisting data to disk on a per-database basis and in multiple ways. There are two options for persistence:  Append Only File (AOF) - A continuous writing of data to disk Snapshot (RDB) - An automatic periodic snapshot writing to disk  Data persistence, via either mechanism, is used solely to rehydrate the database if the database process fails for any reason. It is not a replacement for backups, but something you do in addition to backups. To disable data persistence, select None. AOF writes the latest ‘write’ commands into a file every second, it resembles a traditional RDBMS’s redo log, if you are familiar with that. This file can later be ‘replayed’ in order to recover from a crash. A snapshot (RDB) on the other hand, is performed every one, six, or twelve hours. The snapshot is a dump of the data and while there is a potential of losing up to one hour of data, it is dramatically faster to recover from a snapshot compared to AOF recovery. Persistence can be configured either at time of database creation or by editing an existing database’s configuration. While the persistence model can be changed dynamically, just know that it can take time for your database to switch from one persistence model to the other. It depends on what you are switching from and to, but also on the size of your database. Note: For performance reasons, if you are going to be using AOF, it is highly recommended to make sure replication is enabled for that database as well. When these two features are enabled, persistence is performed\xa0on the database slave and does not impact performance on the master. Options for configuring data persistence There are six\xa0options for persistence in Redis Enterprise Software:    Options Description     None Data is not persisted to disk at all.   Append Only File (AoF) on every write Data is fsynced to disk with every write.   Append Only File (AoF) one second Data is fsynced to disk every second.   Snapshot every 1 hour A snapshot of the database is created every hour.   Snapshot every 6 hours A snapshot of the database is created every 6 hours.   Snapshot every 12 hours A snapshot of the database is created every 12 hours.    The first thing you need to do is determine if you even need persistence. Persistence is used to recover from a catastrophic failure, so make sure that you need to incur the overhead of persistence before you select it. If the database is being used as a cache, then you may not need persistence. If you do need persistence, then you need to identify\xa0which is the best type for your use case. Append only file (AOF) vs snapshot (RDB) Now that you know the available options, to assist in making a decision on which option is right for your use case, here is a table about the two:    Append Only File (AOF) Snapshot (RDB)     More resource intensive Less resource\xa0intensive   Provides better durability (recover the latest point in time) Less durable   Slower time to recover (Larger files) Faster recovery time   More disk space required (files tend to grow large and require compaction) Requires less resource (I/O once every several hours and no compaction required)    Data persistence and Redis on Flash If you are enabling data persistence for databases running on Redis Enterprise Flash, by default both master and slave shards are configured to write to disk. This is unlike a standard Redis Enterprise Software database where only the slave shards persist to disk. This master and slave dual data persistence with replication is done to better protect the database against node failures. Flash-based databases are expected to hold larger datasets and repair times for shards can be longer under node failures. Having dual-persistence provides better protection against failures under these longer repair times. However, the dual data persistence with replication adds some processor and network overhead, especially in the case of cloud configurations with persistent storage that is network attached (e.g. EBS-backed volumes in AWS). There may be times where performance is critical for your use case and you don’t want to risk data persistence adding latency. If that is the case, you can disable data-persistence on the master shards using the following\xa0rladmin command: rladmin tune db db: master_persistence disabled     Page Contents   Options for configuring data persistence   Append only file (AOF) vs snapshot (RDB)   Data persistence and Redis on Flash',
        'type': 'page',
        'position': 0,
        '__score': 1
    }
    key = keys.document(DOCS_PROD.url, expected_doc['doc_id'])
    indexer.search_client.redis.hset.call_args_list[0] = call(key, mapping=expected_doc)


def test_indexer_indexes_page_section_documents(index_file, keys):
    """
    Test indexing page sections.

    NOTE: If this test fails, it may be that you changed the fixture HTML.
    Changing the HTML may cause the test to fail because the MD5 hash of
    the HTML will change, thus the "doc_id" will be different. If this happens,
    you can find the new hash by adding `import ipdb; ipdb.set_trace()` into
    this test and running the tests with the `-s` flag. Then check the value
    of the mock calls, e.g.:
    
        ipdb> indexer.search_client.redis.hset.call_args_list[3]
        call('<key>', mapping={'doc_id': 'https://docs.redislabs.com/latest//test:section:c63108b05d076d2cdff93c6065bf362e', ... )
    """
    indexer = index_file(FILE_WITH_SECTIONS)
    expected_section_docs = [{
        'doc_id': f'{TEST_URL}:section:299d6e11b67f34e8a0d84347ae5efbd7',
        'title': 'Database Persistence with Redis Enterprise Software',
        'section_title': 'Options for configuring data persistence',
        'hierarchy': '[]',
        'url': TEST_URL,
        's': 'test',
        'body':
        'There are six\xa0options for persistence in Redis Enterprise Software:    Options Description     None Data is not persisted to disk at all.   Append Only File (AoF) on every write Data is fsynced to disk with every write.   Append Only File (AoF) one second Data is fsynced to disk every second.   Snapshot every 1 hour A snapshot of the database is created every hour.   Snapshot every 6 hours A snapshot of the database is created every 6 hours.   Snapshot every 12 hours A snapshot of the database is created every 12 hours.    The first thing you need to do is determine if you even need persistence. Persistence is used to recover from a catastrophic failure, so make sure that you need to incur the overhead of persistence before you select it. If the database is being used as a cache, then you may not need persistence. If you do need persistence, then you need to identify\xa0which is the best type for your use case.',
        'type': 'section',
        'position': 0,
        '__score': 0.75,
    }, {
        'doc_id': f'{TEST_URL}:section:f62925eb9d8dca6774a8db54459cf716',
        'title': 'Database Persistence with Redis Enterprise Software',
        'section_title': 'Append only file (AOF) vs snapshot (RDB)',
        'hierarchy': '[]',
        'url': TEST_URL,
        's': 'test',
        'body':
        'Now that you know the available options, to assist in making a decision on which option is right for your use case, here is a table about the two:    Append Only File (AOF) Snapshot (RDB)     More resource intensive Less resource\xa0intensive   Provides better durability (recover the latest point in time) Less durable   Slower time to recover (Larger files) Faster recovery time   More disk space required (files tend to grow large and require compaction) Requires less resource (I/O once every several hours and no compaction required)',
        'type': 'section',
        'position': 1,
        '__score': 0.75,
    }, {
        'doc_id': f'{TEST_URL}:section:c63108b05d076d2cdff93c6065bf362e',
        'title': 'Database Persistence with Redis Enterprise Software',
        'section_title': 'Data persistence and Redis on Flash with Active\\-Active',
        's': 'test',
        'hierarchy': '[]',
        'url': TEST_URL,
        'body':
        'active\\-active If you are enabling data persistence for databases running on Redis Enterprise Flash, by default both master and slave shards are configured to write to disk. This is unlike a standard Redis Enterprise Software database where only the slave shards persist to disk. This master and slave dual data persistence with replication is done to better protect the database against node failures. Flash-based databases are expected to hold larger datasets and repair times for shards can be longer under node failures. Having dual-persistence provides better protection against failures under these longer repair times. However, the dual data persistence with replication adds some processor and network overhead, especially in the case of cloud configurations with persistent storage that is network attached (e.g. EBS-backed volumes in AWS). There may be times where performance is critical for your use case and you don’t want to risk data persistence adding latency. If that is the case, you can disable data-persistence on the master shards using the following\xa0rladmin command: rladmin tune db db: master_persistence disabled',
        'type': 'section',
        'position': 2,
        '__score': 0.75
    }]

    # Ignore the first call, which is for the page. In this test,
    # we're focused on the section documents
    for i, doc in enumerate(expected_section_docs, start=1):
        key = keys.document(DOCS_PROD.url, doc['doc_id'])
        assert indexer.search_client.redis.hset.call_args_list[i] == call(key, mapping=doc)


def test_document_parser_skips_pages_without_title(parse_file):
    with pytest.raises(ParseError):
        parse_file(FILE_WITHOUT_TITLE)


def test_document_parser_skips_release_notes(parse_file):
    with pytest.raises(ParseError):
        parse_file(FILE_RELEASE_NOTES)


def test_parsing_page_with_links_in_h2s_returns_body_content(parse_file):
    """A regression test."""
    docs = parse_file(FILE_WITH_AN_INDEX)
    for doc in docs:
        assert doc.body is not None


def test_build_hierarchy(indexer):
    indexer.seen_urls = {
        "https://docs.redislabs.com/latest/1": "One",
        "https://docs.redislabs.com/latest/1/2": "Two",
        "https://docs.redislabs.com/latest/1/2/3": "Three",
    }
    doc = SearchDocument(doc_id="123",
                         title="Title",
                         section_title="Section",
                         hierarchy=[],
                         s="",
                         url="https://docs.redislabs.com/latest/1/2/3/",
                         body="This is the body",
                         type='page',
                         position=0)
    assert indexer.build_hierarchy(doc) == ['One', 'Two', 'Three']


def test_indexer_indexes_sections_from_h3s(index_file, keys):
    indexer = index_file(FILE_WITH_H3s)

    expected_section_docs = [{
        'doc_id': f'{TEST_URL}:page:5a6938363f1cb38ef2eec5397c4e67cc',
        'title': 'RedisBloom Tutorial',
        'section_title': '',
        'hierarchy': '[]',
        'url': 'https://docs.redislabs.com/latest//test',
        'body':
        'RedisBloom Tutorial | Redis Developer Hub                                  Skip to main content                  Get started Try Free    🌜   🌞                    Get started   Try Free              Menu      Home   Create   Overview   Redis Enterprise Cloud   Redis on Heroku   Redis on Azure Cache   Redis on Google Cloud   Redis on AWS   Redis on Docker   Redis on Kubernetes   Redis from Source     Develop   Overview   Java   Python   Node.js   Go   Ruby   Php     Explore   Overview   RedisInsight   Redis Data Source for Grafana   RedisMod   RIOT     HowTos & Tutorials   Overview   RediSearch Tutorial   RedisJSON Tutorial   RedisTimeSeries Tutorial   RedisGraph Tutorial   RedisBloom Tutorial   RedisGears Tutorial   How to build a Shopping cart app using NodeJS and RedisJSON   How to build a Real-Time Leaderboard app Using Redis   How to build a Rate Limiter using Redis   How to cache REST API responses Using Redis & NodeJS   How to list & search Movies database using RediSearch   1. Getting Started   2. Install Redisearch   3. Create Index   4. Query Data   5. Manage Index   6. Import datasets   7. Query Movies   8. Aggregation   9. Advanced Option   10. Sample Application                 RedisBloom Tutorial   RedisBloom extends Redis core to support additional probabilistic data structures. It allows for solving computer science problems in a constant memory space with extremely fast processing and a low error rate. It supports scalable Bloom and Cuckoo filters to determine (with a specified degree of certainty) whether an item is present or absent from a collection.  The RedisBloom module provides four data types:  Bloom filter: A probabilistic data structure that can test for presence. A Bloom filter is a data structure designed to tell you, rapidly and memory-efficiently, whether an element is present in a set. Bloom filters typically exhibit better performance and scalability when inserting items (so if you\'re often adding items to your dataset then Bloom may be ideal).  Cuckoo filter: An alternative to Bloom filters, Cuckoo filters comes with additional support for deletion of elements from a set. These filters are quicker on check operations. Count-min sketch: A count-min sketch is generally used to determine the frequency of events in a stream. You can query the count-min sketch to get an estimate of the frequency of any given event.   Top-K: The Top-k probabilistic data structure in RedisBloom is a deterministic algorithm that approximates frequencies for the top k items. With Top-K, you’ll be notified in real time whenever elements enter into or are expelled from your Top-K list. If an element add-command enters the list, the dropped element will be returned.                                                     Step 1. Register and subscribe                                                                                                     Follow                                                  this link to register                                                  and subscribe to Redis Enterprise Cloud                                                                                                   Step 2. Create a database with RedisBloom Module                                                                                                         Step 3. Connect to a database                                                                                                     Follow                                                  this                                                  link to know how to connect to a database                                                                                                Step 4. Getting Started with RedisBloom                                                    In the next steps you will use some basic RedisBloom commands. You can run them from the Redis command-line interface (redis-cli) or use the CLI available in RedisInsight. (See part 2 of this tutorial to learn more about using the RedisInsight CLI.) To interact with RedisBloom, you use the BF.ADD and BF.EXISTS commands.  Let’s go ahead and test drive some RedisBloom-specific operations. We will create a basic dataset based on unique visitors’ IP addresses, and you will see how to:  Create a Bloom filter Determine whether or not an item exists in the Bloom filter Add one or more items to the Bloom filter Determine whether or not a unique visitor’s IP address exists  Let’s walk through the process step-by-step:                                                   Create a Bloom filter                                                    Use the BF.ADD command to add a unique visitor IP address to the Bloom filter as shown here:      >> BF.ADD unique_visitors 10.94.214.120   (integer) 1   (1.75s)    Copy                                                     Determine whether or not an item exists                                                    Use the BF.EXISTS command to determine whether or not an item may exist in the Bloom filter:      >> BF.EXISTS unique_visitors 10.94.214.120   (integer) 1    Copy        >> BF.EXISTS unique_visitors 10.94.214.121   (integer) 0   (1.46s)    Copy   In the above example, the first command shows the result as “1”, indicating that the item may exist, whereas the second command displays "0", indicating that the item certainly may not exist.                                                   Add one or more items to the Bloom filter                                                    Use the BF.MADD command to add one or more items to the Bloom filter, creating the filter if it does not yet exist. This command operates identically to BF.ADD, except it allows multiple inputs and returns multiple values:      >> BF.MADD unique_visitors 10.94.214.100 10.94.214.200 10.94.214.210 10.94.214.212   1) (integer) 1   2) (integer) 1   3) (integer) 1   4) (integer) 1    Copy   As shown above, the BF.MADD allows you to add one or more visitors’ IP addresses to the Bloom filter.                                                   Determine whether or not a unique visitor’s IP address exists                                                    Use BF.MEXISTS to determine if one or more items may exist in the filter or not:      >> BF.MEXISTS unique_visitors 10.94.214.200 10.94.214.212   1) (integer) 1   2) (integer) 1    Copy         >> BF.MEXISTS unique_visitors 10.94.214.200 10.94.214.213   1) (integer) 1   2) (integer) 0    Copy   In the above example, the first command shows the result as “1” for both the visitors’ IP addresses, indicating that these items do exist. The second command displays "0" for one of the visitor’s IP addresses, indicating that the item certainly does not exist.                                                   Next Step                                                                                                          Learn more about RedisBloom in the                                                      Quick Start                                                      tutorial.                                                                                                                  Edit this page                                                         Previous « RedisGraph Tutorial     Next RedisGears Tutorial »           Step 1. Register and subscribe   Step 2. Create a database with RedisBloom Module   Step 3. Connect to a database   Step 4. Getting Started with RedisBloom   Next Step                         Made with </> by         Get Started   Create Database   Develop   Explore your data   Best Practices   Build with Redis Modules     Resources   Community   Redis University   Command Reference   How-tos & tutorials       Copyright: © 2021 Redis Labs. Redis and the cube logo are registered trademarks of Redis Labs Ltd.',
        'type': 'page',
        's': 'test',
        'position': 0,
        '__score': 1.0
    }, {
        'doc_id': f'{TEST_URL}:section:113820cc765e7328919bc24f7847482c',
        'title': 'RedisBloom Tutorial',
        'section_title': '',
        'hierarchy': '[]',
        'url': 'https://docs.redislabs.com/latest//test',
        'body':
        'Follow                                                  this link to register                                                  and subscribe to Redis Enterprise Cloud                                                                                                   Step 2. Create a database with RedisBloom Module                                                 #                                                       Step 3. Connect to a database                                                 #                                                   Follow                                                  this                                                  link to know how to connect to a database                                                                                                Step 4. Getting Started with RedisBloom                                                 #  In the next steps you will use some basic RedisBloom commands. You can run them from the Redis command-line interface (redis-cli) or use the CLI available in RedisInsight. (See part 2 of this tutorial to learn more about using the RedisInsight CLI.) To interact with RedisBloom, you use the BF.ADD and BF.EXISTS commands.  Let’s go ahead and test drive some RedisBloom-specific operations. We will create a basic dataset based on unique visitors’ IP addresses, and you will see how to:  Create a Bloom filter Determine whether or not an item exists in the Bloom filter Add one or more items to the Bloom filter Determine whether or not a unique visitor’s IP address exists  Let’s walk through the process step-by-step:                                                   Create a Bloom filter                                                 #  Use the BF.ADD command to add a unique visitor IP address to the Bloom filter as shown here:      >> BF.ADD unique_visitors 10.94.214.120   (integer) 1   (1.75s)    Copy                                                     Determine whether or not an item exists                                                 #  Use the BF.EXISTS command to determine whether or not an item may exist in the Bloom filter:      >> BF.EXISTS unique_visitors 10.94.214.120   (integer) 1    Copy        >> BF.EXISTS unique_visitors 10.94.214.121   (integer) 0   (1.46s)    Copy   In the above example, the first command shows the result as “1”, indicating that the item may exist, whereas the second command displays "0", indicating that the item certainly may not exist.                                                   Add one or more items to the Bloom filter                                                 #  Use the BF.MADD command to add one or more items to the Bloom filter, creating the filter if it does not yet exist. This command operates identically to BF.ADD, except it allows multiple inputs and returns multiple values:      >> BF.MADD unique_visitors 10.94.214.100 10.94.214.200 10.94.214.210 10.94.214.212   1) (integer) 1   2) (integer) 1   3) (integer) 1   4) (integer) 1    Copy   As shown above, the BF.MADD allows you to add one or more visitors’ IP addresses to the Bloom filter.                                                   Determine whether or not a unique visitor’s IP address exists                                                 #  Use BF.MEXISTS to determine if one or more items may exist in the filter or not:      >> BF.MEXISTS unique_visitors 10.94.214.200 10.94.214.212   1) (integer) 1   2) (integer) 1    Copy         >> BF.MEXISTS unique_visitors 10.94.214.200 10.94.214.213   1) (integer) 1   2) (integer) 0    Copy   In the above example, the first command shows the result as “1” for both the visitors’ IP addresses, indicating that these items do exist. The second command displays "0" for one of the visitor’s IP addresses, indicating that the item certainly does not exist.                                                   Next Step                                                 #                                                        Learn more about RedisBloom in the                                                      Quick Start                                                      tutorial.',
        'type': 'section',
        's': 'test',
        'position': 0,
        '__score': 0.75
    }, {
        'doc_id': f'{TEST_URL}:section:0c0fe866d8e3ee6b792aed7c3738f4f6',
        'title': 'RedisBloom Tutorial',
        'section_title': '',
        'hierarchy': '[]',
        'url': 'https://docs.redislabs.com/latest//test',
        'body':
        'Step 3. Connect to a database                                                 #                                                   Follow                                                  this                                                  link to know how to connect to a database                                                                                                Step 4. Getting Started with RedisBloom                                                 #  In the next steps you will use some basic RedisBloom commands. You can run them from the Redis command-line interface (redis-cli) or use the CLI available in RedisInsight. (See part 2 of this tutorial to learn more about using the RedisInsight CLI.) To interact with RedisBloom, you use the BF.ADD and BF.EXISTS commands.  Let’s go ahead and test drive some RedisBloom-specific operations. We will create a basic dataset based on unique visitors’ IP addresses, and you will see how to:  Create a Bloom filter Determine whether or not an item exists in the Bloom filter Add one or more items to the Bloom filter Determine whether or not a unique visitor’s IP address exists  Let’s walk through the process step-by-step:                                                   Create a Bloom filter                                                 #  Use the BF.ADD command to add a unique visitor IP address to the Bloom filter as shown here:      >> BF.ADD unique_visitors 10.94.214.120   (integer) 1   (1.75s)    Copy                                                     Determine whether or not an item exists                                                 #  Use the BF.EXISTS command to determine whether or not an item may exist in the Bloom filter:      >> BF.EXISTS unique_visitors 10.94.214.120   (integer) 1    Copy        >> BF.EXISTS unique_visitors 10.94.214.121   (integer) 0   (1.46s)    Copy   In the above example, the first command shows the result as “1”, indicating that the item may exist, whereas the second command displays "0", indicating that the item certainly may not exist.                                                   Add one or more items to the Bloom filter                                                 #  Use the BF.MADD command to add one or more items to the Bloom filter, creating the filter if it does not yet exist. This command operates identically to BF.ADD, except it allows multiple inputs and returns multiple values:      >> BF.MADD unique_visitors 10.94.214.100 10.94.214.200 10.94.214.210 10.94.214.212   1) (integer) 1   2) (integer) 1   3) (integer) 1   4) (integer) 1    Copy   As shown above, the BF.MADD allows you to add one or more visitors’ IP addresses to the Bloom filter.                                                   Determine whether or not a unique visitor’s IP address exists                                                 #  Use BF.MEXISTS to determine if one or more items may exist in the filter or not:      >> BF.MEXISTS unique_visitors 10.94.214.200 10.94.214.212   1) (integer) 1   2) (integer) 1    Copy         >> BF.MEXISTS unique_visitors 10.94.214.200 10.94.214.213   1) (integer) 1   2) (integer) 0    Copy   In the above example, the first command shows the result as “1” for both the visitors’ IP addresses, indicating that these items do exist. The second command displays "0" for one of the visitor’s IP addresses, indicating that the item certainly does not exist.                                                   Next Step                                                 #                                                        Learn more about RedisBloom in the                                                      Quick Start                                                      tutorial.',
        'type': 'section',
        's': 'test',
        'position': 1,
        '__score': 0.75
    }, {
        'doc_id': f'{TEST_URL}:section:2178f498278a818fa1e0b08206a2347e',
        'title': 'RedisBloom Tutorial',
        'section_title': '',
        'hierarchy': '[]',
        'url': 'https://docs.redislabs.com/latest//test',
        'body':
        'Follow                                                  this                                                  link to know how to connect to a database                                                                                                Step 4. Getting Started with RedisBloom                                                 #  In the next steps you will use some basic RedisBloom commands. You can run them from the Redis command-line interface (redis-cli) or use the CLI available in RedisInsight. (See part 2 of this tutorial to learn more about using the RedisInsight CLI.) To interact with RedisBloom, you use the BF.ADD and BF.EXISTS commands.  Let’s go ahead and test drive some RedisBloom-specific operations. We will create a basic dataset based on unique visitors’ IP addresses, and you will see how to:  Create a Bloom filter Determine whether or not an item exists in the Bloom filter Add one or more items to the Bloom filter Determine whether or not a unique visitor’s IP address exists  Let’s walk through the process step-by-step:                                                   Create a Bloom filter                                                 #  Use the BF.ADD command to add a unique visitor IP address to the Bloom filter as shown here:      >> BF.ADD unique_visitors 10.94.214.120   (integer) 1   (1.75s)    Copy                                                     Determine whether or not an item exists                                                 #  Use the BF.EXISTS command to determine whether or not an item may exist in the Bloom filter:      >> BF.EXISTS unique_visitors 10.94.214.120   (integer) 1    Copy        >> BF.EXISTS unique_visitors 10.94.214.121   (integer) 0   (1.46s)    Copy   In the above example, the first command shows the result as “1”, indicating that the item may exist, whereas the second command displays "0", indicating that the item certainly may not exist.                                                   Add one or more items to the Bloom filter                                                 #  Use the BF.MADD command to add one or more items to the Bloom filter, creating the filter if it does not yet exist. This command operates identically to BF.ADD, except it allows multiple inputs and returns multiple values:      >> BF.MADD unique_visitors 10.94.214.100 10.94.214.200 10.94.214.210 10.94.214.212   1) (integer) 1   2) (integer) 1   3) (integer) 1   4) (integer) 1    Copy   As shown above, the BF.MADD allows you to add one or more visitors’ IP addresses to the Bloom filter.                                                   Determine whether or not a unique visitor’s IP address exists                                                 #  Use BF.MEXISTS to determine if one or more items may exist in the filter or not:      >> BF.MEXISTS unique_visitors 10.94.214.200 10.94.214.212   1) (integer) 1   2) (integer) 1    Copy         >> BF.MEXISTS unique_visitors 10.94.214.200 10.94.214.213   1) (integer) 1   2) (integer) 0    Copy   In the above example, the first command shows the result as “1” for both the visitors’ IP addresses, indicating that these items do exist. The second command displays "0" for one of the visitor’s IP addresses, indicating that the item certainly does not exist.                                                   Next Step                                                 #                                                        Learn more about RedisBloom in the                                                      Quick Start                                                      tutorial.',
        'type': 'section',
        's': 'test',
        'position': 2,
        '__score': 0.75
    }, {
        'doc_id': f'{TEST_URL}:section:f7eef8eb8ad1b02ab6f269da416ae08a',
        'title': 'RedisBloom Tutorial',
        'section_title': '',
        'hierarchy': '[]',
        'url': 'https://docs.redislabs.com/latest//test',
        'body':
        'In the next steps you will use some basic RedisBloom commands. You can run them from the Redis command-line interface (redis-cli) or use the CLI available in RedisInsight. (See part 2 of this tutorial to learn more about using the RedisInsight CLI.) To interact with RedisBloom, you use the BF.ADD and BF.EXISTS commands.  Let’s go ahead and test drive some RedisBloom-specific operations. We will create a basic dataset based on unique visitors’ IP addresses, and you will see how to:  Create a Bloom filter Determine whether or not an item exists in the Bloom filter Add one or more items to the Bloom filter Determine whether or not a unique visitor’s IP address exists  Let’s walk through the process step-by-step:                                                   Create a Bloom filter                                                 #  Use the BF.ADD command to add a unique visitor IP address to the Bloom filter as shown here:      >> BF.ADD unique_visitors 10.94.214.120   (integer) 1   (1.75s)    Copy                                                     Determine whether or not an item exists                                                 #  Use the BF.EXISTS command to determine whether or not an item may exist in the Bloom filter:      >> BF.EXISTS unique_visitors 10.94.214.120   (integer) 1    Copy        >> BF.EXISTS unique_visitors 10.94.214.121   (integer) 0   (1.46s)    Copy   In the above example, the first command shows the result as “1”, indicating that the item may exist, whereas the second command displays "0", indicating that the item certainly may not exist.                                                   Add one or more items to the Bloom filter                                                 #  Use the BF.MADD command to add one or more items to the Bloom filter, creating the filter if it does not yet exist. This command operates identically to BF.ADD, except it allows multiple inputs and returns multiple values:      >> BF.MADD unique_visitors 10.94.214.100 10.94.214.200 10.94.214.210 10.94.214.212   1) (integer) 1   2) (integer) 1   3) (integer) 1   4) (integer) 1    Copy   As shown above, the BF.MADD allows you to add one or more visitors’ IP addresses to the Bloom filter.                                                   Determine whether or not a unique visitor’s IP address exists                                                 #  Use BF.MEXISTS to determine if one or more items may exist in the filter or not:      >> BF.MEXISTS unique_visitors 10.94.214.200 10.94.214.212   1) (integer) 1   2) (integer) 1    Copy         >> BF.MEXISTS unique_visitors 10.94.214.200 10.94.214.213   1) (integer) 1   2) (integer) 0    Copy   In the above example, the first command shows the result as “1” for both the visitors’ IP addresses, indicating that these items do exist. The second command displays "0" for one of the visitor’s IP addresses, indicating that the item certainly does not exist.                                                   Next Step                                                 #                                                        Learn more about RedisBloom in the                                                      Quick Start                                                      tutorial.',
        'type': 'section',
        's': 'test',
        'position': 3,
        '__score': 0.75
    }, {
        'doc_id': f'{TEST_URL}:section:14094b624de5c096352862568e38516c',
        'title': 'RedisBloom Tutorial',
        'section_title': '',
        'hierarchy': '[]',
        'url': 'https://docs.redislabs.com/latest//test',
        'body':
        'Learn more about RedisBloom in the                                                      Quick Start                                                      tutorial.',
        'type': 'section',
        's': 'test',
        'position': 4,
        '__score': 0.75
    }]

    for i, doc in enumerate(expected_section_docs):
        key = keys.document(DOCS_PROD.url, doc['doc_id'])
        assert indexer.search_client.redis.hset.call_args_list[i] == call(
            key, mapping=doc)
