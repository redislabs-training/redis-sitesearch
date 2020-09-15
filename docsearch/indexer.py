import concurrent.futures
import json
from dataclasses import asdict
from typing import List, Any, Dict, Tuple

import redis.exceptions
from redis import Redis
from redisearch import TextField, Client
from bs4 import BeautifulSoup, element

from docsearch.errors import ParseError
from docsearch.models import SearchDocument, TYPE_PAGE, TYPE_SECTION
from docsearch.validators import skip_release_notes

ROOT_PAGE = "Redis Labs Documentation"

DEFAULT_VALIDATORS = (
    skip_release_notes,
)

DEFAULT_SCHEMA = (
    TextField("title", weight=1.5),
    TextField("section_title", weight=1.2),
    TextField("url"),
    TextField("body", weight=2),
)


def prepare_text(text: str) -> str:
    return text.strip().strip("\n").replace("\n", " ")


def extract_parts(doc, h2s: List[element.Tag]):
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

        body = prepare_text(BeautifulSoup('\n'.join(page), 'html.parser').get_text())
        _id = f"{doc.url}:{doc.title}:{part_title}:{i}"

        docs.append(SearchDocument(
            doc_id=_id,
            title=doc.title,
            hierarchy=doc.hierarchy,
            section_title=part_title or "",
            body=body,
            url=doc.url,
            type=TYPE_SECTION,
            position=i))

    return docs


def extract_hierarchy(soup):
    """
    Extract the page hierarchy we need from the page's breadcrumbs:
    root and parent page.

    E.g. for the breadcrumbs:
            RedisInsight > Using RedisInsight > Cluster Management

    We want:
            ["RedisInsight", "Using RedisInsight", "Cluster Management"]
    """
    return [a.get_text() for a in soup.select("#breadcrumbs a")
            if a.get_text() != ROOT_PAGE]


def prepare_document(html: str) -> List[SearchDocument]:
    docs = []
    soup = BeautifulSoup(html, 'html.parser')

    try:
        title = prepare_text(soup.title.string.split("|")[0])
    except AttributeError:
        raise (ParseError(f"Failed -- missing title"))

    try:
        url = soup.find_all("link", attrs={"rel": "canonical"})[0].attrs['href']
    except IndexError:
        raise ParseError(f"Failed -- missing link")

    hierarchy = extract_hierarchy(soup)

    if not hierarchy:
        raise ParseError(f"Failed -- missing breadcrumbs")

    content = soup.select(".main-content")

    # Try to index only the content div. If a page lacks
    # that div, index the entire thing.
    if content:
        content = content[0]
    else:
        content = soup

    h2s = content.find_all('h2')
    body = prepare_text(content.get_text())
    doc = SearchDocument(
        doc_id=f"{url}:{title}",
        title=title,
        section_title="",
        hierarchy=hierarchy,
        body=body,
        url=url,
        type=TYPE_PAGE)

    # Index the entire document
    docs.append(doc)

    # If there are headers, break up the document and index each header
    # as a separate document.
    if h2s:
        docs += extract_parts(doc, h2s)

    return docs


def document_to_dict(document: SearchDocument):
    """
    Given a SearchDocument, return a dictionary of the fields to index,
    and options like the ad-hoc score.
    """
    doc = asdict(document)
    if document.type == TYPE_PAGE:
        # Score pages lower than page sections.
        doc['score'] = 0.5
    doc['hierarchy'] = json.dumps(doc['hierarchy'])
    return doc


def add_document(search_client, doc: SearchDocument):
    search_client.add_document(**document_to_dict(doc))


def prepare_file(file) -> List[SearchDocument]:
    print(f"parsing file {file}")
    with open(file) as f:
        return prepare_document(f.read())


class Indexer:
    def __init__(self, search_client: Client, redis_client: Redis,
                 schema=None, validators=None, create_index=True):
        self.search_client = search_client
        self.redis_client = redis_client

        if validators is None:
            self.validators = DEFAULT_VALIDATORS

        if schema is None:
            self.schema = DEFAULT_SCHEMA

        if create_index:
            self.setup_index()

    def setup_index(self):
        # Creating the index definition and schema
        try:
            self.search_client.info()
        except redis.exceptions.ResponseError:
            pass
        else:
            self.search_client.drop_index()

        self.search_client.create_index(self.schema)

    def validate(self, doc: SearchDocument):
        for v in self.validators:
            v(doc)

    def prepare_files(self, files: List[str]) -> Tuple[List[SearchDocument], List[str]]:
        docs: List[SearchDocument] = []
        errors: List[str] = []

        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []

            for file in files:
                futures.append(executor.submit(prepare_file, file))

            for future in concurrent.futures.as_completed(futures):
                try:
                    docs_for_file = future.result()
                except ParseError as e:
                    errors.append(f"{e}: {file}")
                    continue

                if not docs_for_file:
                    continue

                # If any document we generated for a file fails validation, we
                # intentionally skip the entire file -- the "continue" here
                # applies to the loop over completed futures.
                try:
                    for doc in docs_for_file:
                        self.validate(doc)
                except ParseError as e:
                    errors.append(f"{e}: {file}")
                    continue

                docs += docs_for_file

        return docs, errors

    def index_files(self, files: List[str]) -> List[str]:
        docs, errors = self.prepare_files(files)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []

            for doc in docs:
                futures.append(
                    executor.submit(add_document, self.search_client, doc))

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except redis.exceptions.DataError as e:
                    errors.append(f"Failed -- bad data: {e}")
                    continue
                except redis.exceptions.ResponseError as e:
                    errors.append(f"Failed -- response error: {e}")
                    continue

        return errors
