import glob
import logging
import sys
from queue import Queue
from threading import Thread
from multiprocessing import cpu_count

import click
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher

from docsearch.connections import get_search_connection, get_redis_connection
from docsearch.indexer import Indexer, DocumentationSpider
from docsearch.models import SearchDocument


log = logging.getLogger(__name__)
search_client = get_search_connection()
redis_client = get_redis_connection()
MAX_THREADS = cpu_count() * 5


@click.argument("url" )
@click.command()
def index(url):
    """Index a documentation site URL in RediSearch."""
    docs_to_process = Queue()
    indexer = Indexer(search_client, redis_client)

    class Spider(DocumentationSpider):
        url = url

    def crawler_results(signal, sender, item: SearchDocument, response, spider):
        docs_to_process.put(item)

    def index_document():
        while True:
            doc: SearchDocument = docs_to_process.get()
            log.error("Indexing doc: %s", doc)
            try:
                indexer.index_document(doc)
            except Exception as e:
                log.error("Unexpected error while indexing doc %s, error: %s", doc.doc_id, e)
            docs_to_process.task_done()

    def start_indexing():
        if docs_to_process.empty():
            return
        docs_to_process.join()

    for _ in range(MAX_THREADS):
        Thread(target=index_document, daemon=True).start()

    dispatcher.connect(crawler_results, signal=signals.item_scraped)
    dispatcher.connect(start_indexing, signal=signals.engine_stopped)

    process = CrawlerProcess(settings={
        'CONCURRENT_REQUESTS_PER_DOMAIN': 20,
        'HTTP_CACHE_ENABLED': True,
        'LOG_LEVEL': 'ERROR'
    })
    process.crawl(Spider)
    process.start()
