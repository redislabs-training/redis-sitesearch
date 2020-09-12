from unittest import mock

from docsearch.indexer import Indexer


def test_indexer_indexes_file():
    file = "documents/rs/concepts/data-access/index.html"
    mock_client = mock.MagicMock()
    mock_search_client = mock.MagicMock()
    indexer = Indexer(mock_client, mock_search_client)

    indexer.index_files([file])

    assert mock_search_client.add_document.called
