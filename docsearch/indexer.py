import concurrent.futures
import json
from dataclasses import asdict

import redis.exceptions
from redisearch import TextField
from bs4 import BeautifulSoup

from docsearch.errors import ParseError
from docsearch.models import SearchDocument
from docsearch.validators import skip_release_notes

ROOT_PAGE = "Redis Labs Documentation"

DEFAULT_VALIDATORS = (
    skip_release_notes,
)

DEFAULT_SCHEMA = (
    TextField("title", weight=8.0),
    TextField("section_title", weight=2.0),
    TextField("root_page"),
    TextField("parent_page"),
    TextField("url"),
    TextField("body", weight=1.2)
)


def extract_parts(doc, h2s):
    docs = []

    def next_element(elem):
        while elem is not None:
            elem = elem.next_sibling
            if hasattr(elem, 'name'):
                return elem

    for i, tag in enumerate(h2s):
        # Sometimes we stick the title in as a link...
        if tag and tag.string is None:
            tag = tag.find("a")

        part_title = tag.get_text() if tag else ""

        page = []
        elem = next_element(tag)

        while elem and elem.name != 'h2':
            page.append(str(elem))
            elem = next_element(elem)

        body = BeautifulSoup('\n'.join(page), 'html.parser').get_text()
        _id = f"{doc.url}:{doc.title}:{part_title}:{i}"

        docs.append(SearchDocument(
            doc_id=_id,
            title=doc.title,
            root_page=doc.root_page,
            parent_page=doc.parent_page,
            section_title=part_title or "",
            body=body,
            url=doc.url))

    return docs


def extract_topology(soup):
    """
    Extract the hierarchy we need -- root and parent page.

    E.g. for the topology:
            RedisInsight > Using RedisInsight > Cluster Management

    We want:
            ["RedisInsight", "Using RedisInsight"]
    """
    breadcrumbs = [a.get_text() for a in soup.select("#breadcrumbs a")
                   if a.get_text() != ROOT_PAGE]

    if not breadcrumbs:
        return None, None

    root = breadcrumbs[0]
    parent = breadcrumbs[-1]

    return root, parent


def prepare_document(file):
    docs = []

    print(f"parsing file {file}")

    with open(file) as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    try:
        title = soup.title.string.split("|")[0].strip()
    except AttributeError:
        raise (ParseError(f"Failed -- missing title: {file}"))

    try:
        url = soup.find_all("link", attrs={"rel": "canonical"})[0].attrs['href']
    except IndexError:
        raise ParseError(f"Failed -- missing link: {file}")

    root, parent = extract_topology(soup)

    if not root:
        raise ParseError(f"Failed -- missing breadcrumbs: {file}")

    content = soup.select(".main-content")

    # Try to index only the content div. If a page lacks
    # that div, index the entire thing.
    if content:
        content = content[0]
    else:
        content = soup

    h2s = content.find_all('h2')
    body = content.get_text()
    doc = SearchDocument(
        doc_id=f"{url}:{title}",
        title=title,
        section_title="",
        root_page=root,
        parent_page=parent,
        body=body,
        url=url)

    # If there are headers, break up the document and index each header
    # as a separate document.
    if h2s:
        docs += extract_parts(doc, h2s)
    else:
        # Index the entire document
        docs.append(doc)

    return docs


class Indexer:
    def __init__(self, redis_client, schema=None, validators=None):
        self.client = redis_client

        if validators is None:
            self.validators = DEFAULT_VALIDATORS

        if schema is None:
            self.schema = DEFAULT_SCHEMA

        self.setup_index()

    def setup_index(self):
        # Creating the index definition and schema
        try:
            self.client.info()
        except redis.exceptions.ResponseError:
            pass
        else:
            self.client.drop_index()

        self.client.create_index(self.schema)

    def validate(self, doc):
        for v in self.validators:
            v(doc)

    def prepare_documents(self, files):
        docs = []
        errors = []

        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []

            for file in files:
                futures.append(executor.submit(prepare_document, file))

            for future in concurrent.futures.as_completed(futures):
                try:
                    docs_for_file = future.result()
                except ParseError as e:
                    errors.append(str(e))
                    continue

                if not docs_for_file:
                    continue

                try:
                    for doc in docs_for_file:
                        self.validate(doc)
                except ParseError as e:
                    errors.append(str(e))
                    continue

                docs += docs_for_file

        return docs, errors

    def index_files(self, files):
        docs, errors = self.prepare_documents(files)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []

            for doc in docs:
                futures.append(executor.submit(self.client.add_document, **asdict(doc)))

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except redis.exceptions.DataError as e:
                    errors.append(f"Failed -- bad data: {e}")
                    continue
                except redis.exceptions.ResponseError:
                    errors.append(f"Failed -- already exists: {e}")
                    continue

        return errors
