import time

import pytest


@pytest.mark.skip("This does not work properly in test at the moment.")
def test_no_content(client):
    result = client.simulate_get('/health')
    assert result.status_code == 503


@pytest.mark.skip("This does not work properly in test at the moment.")
def test_with_content(docs, client):
    result = client.simulate_get('/health')
    assert result.status_code == 200
