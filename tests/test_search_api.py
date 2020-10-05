import time


def test_query_python(docs, client):
    result = client.simulate_get('/search?q=*')
    assert result.status_code == 200
    assert result.json['total'] > 0

    titles = [doc['title'] for doc in result.json['results']]
    assert 'Database Persistence with Redis Enterprise Software' in titles


def test_cloud_landing_page(client):
    result = client.simulate_get('/search?q=cloud')
    assert result.json['results'][0]['title'] == 'Redis Enterprise Cloud'
    assert result.json['results'][0]['url'] == 'https://docs.redislabs.com/staging/docs-with-RediSearch/latest/rc/'
