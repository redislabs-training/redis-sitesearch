from falcon import testing

import pytest

from docsearch.api.app import create_app


@pytest.fixture()
def client():
    return testing.TestClient(create_app())


def test_query_python(client):
    result = client.simulate_get('/search?q=python')
    assert result.status_code == 200
    assert result.json['total'] > 0

    titles = [doc['title'] for doc in result.json['results']]
    assert 'Testing Client Connectivity' in titles


def test_cloud_landing_page(client):
    result = client.simulate_get('/search?q=cloud')
    assert result.json['results'][0]['title'] == 'Redis Enterprise Cloud'
