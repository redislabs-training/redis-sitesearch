from redisearch import Document
from docsearch.models import TYPE_PAGE
from docsearch.transformer import transform_documents


def test_transform_documents_elides_body_if_longer_than_max():
    doc = Document(
        id="123",
        title="Title",
        section_title="Section",
        hierarchy='["one","two"]',
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    docs = transform_documents([doc], 5)

    assert docs[0]['body'] == "This ..."


def test_transform_documents_retains_body_if_shorter_than_max():
    doc = Document(
        id="123",
        title="Title",
        section_title="Section",
        hierarchy='["one","two"]',
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    docs = transform_documents([doc])

    assert docs[0]['body'] == "This is the body"


def test_transform_documents_decodes_hierarchy():
    doc = Document(
        id="123",
        title="Title",
        section_title="Section",
        hierarchy='["one","two"]',
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    docs = transform_documents([doc])

    assert docs[0]['hierarchy'] == ["one", "two"]


def test_transform_documents_raises_parse_error_with_bad_hierarchy():
    doc = Document(
        id="123",
        title="Title",
        section_title="Section",
        hierarchy='bad json',
        url="http://example.com/1",
        body="This is the body",
        type=TYPE_PAGE,
        position=0
    )

    docs = transform_documents([doc])

    assert docs[0]['hierarchy'] == []