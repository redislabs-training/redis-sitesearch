import time


def test_no_content(client):
    result = client.simulate_get('/health')
    assert result.status_code == 503


def test_with_content(docs, client):
    time.sleep(5)
    # Should be finished indexing after 5 seconds!
    result = client.simulate_get('/health')
    assert result.status_code == 200
