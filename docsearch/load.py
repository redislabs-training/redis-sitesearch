import glob
import sys
import concurrent.futures
import json

import click
import redis.exceptions
from redisearch import Client, TextField, TagField
from bs4 import BeautifulSoup


# Creating a client with a given index name
client = Client("docs")
ROOT_PAGE = "Redis Labs Documentation"


def setup_index():
    # Creating the index definition and schema
    try:
        client.info()
    except redis.exceptions.ResponseError:
        pass
    else:
        client.drop_index()

    client.create_index(
        (TextField("title", weight=8.0),
        TextField("section_title", weight=2.0),
        TextField("root_page"),
        TextField("parent_page"),
        TextField("url"),
        TextField("body", weight=1.2)))


def extract_parts(title, url, root, parent, h2s):
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

        part_title = tag.string if tag else ""

        page = []
        elem = next_element(tag)

        while elem and elem.name != 'h2':
            page.append(str(elem))
            elem = next_element(elem)

        body = BeautifulSoup('\n'.join(page), 'html.parser').get_text()
        _id = f"{url}:{title}:{part_title}:{i}"

        docs.append({
            "doc_id": _id,
            "title": title,
            "root_page": root,
            "parent_page": parent,
            "section_title": part_title or "",
            "body": body,
            "url": url
        })

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


class ParseError(Exception):
    """An error parsing a file"""


def validate(title):
    if 'Release Notes' in title and not '2020' in title:
        raise ParseError("Skipping outdated release notes")


def prepare_document(file):
    docs = []

    print(f"parsing file {file}")

    with open(file) as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    try:
        title = soup.title.string.split("|")[0].strip()
    except AttributeError:
        raise(ParseError(f"Failed -- missing title: {file}"))

    # Skip indexing old release notes
    validate(title)

    try:
        url = soup.find_all("link", attrs={"rel": "canonical"})[0].attrs['href']
    except IndexError:
        raise ParseError(f"Failed -- missing link: {file}")

    root, parent = extract_topology(soup)

    if not root:
        raise ParseError(f"Failed -- missing breadcrumbs: {file}")

    content = soup.select(".main-content")

    # Try to index only the content div. However, if a page lacks
    # that div, index the entire thing.
    if content:
        content = content[0]
    else:
        content = soup

    # If there are headers, break up the document and index each header
    # as a separate document.
    h2s = content.find_all('h2')

    if h2s:
        docs += extract_parts(title, url, root, parent, h2s)
    else:
        # Index the entire document
        docs.append({
            "doc_id": f"{url}:{title}",
            "title": title,
            "section_title": "",
            "root_page": root,
            "parent_page": parent,
            "body": content.get_text(),
            "url": url
        })

    return json.dumps(docs)


def prepare_documents(files):
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

            docs += json.loads(docs_for_file)

    return docs, errors


@click.option(
    "-d",
    "--directory",
    help="A directory containing HTML files to load into the index",
    multiple=True)
@click.option(
    "-f",
    "--file",
    help="The path to an HTML file to load into the index",
    multiple=True)
@click.command()
def load(directory, file):
    all_files = []

    if not directory and not file:
        sys.exit("Error: please specify a file or directory to load")

    if directory:
        for _dir in directory:
            all_files += glob.glob(_dir + '/**/*.html', recursive=True)
    if file:
        all_files += file

    setup_index()
    docs, errors = prepare_documents(all_files)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for doc in docs:
            futures.append(executor.submit(client.add_document, **doc))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except redis.exceptions.DataError as e:
                errors.append(f"Failed -- bad data: {file}")
                continue
            except redis.exceptions.ResponseError:
                errors.append(f"Failed -- already exists: {file}, {doc['doc_id']}")
                continue

    if errors:
        print("Errors:")
        for error in errors:
            print(str(error))
