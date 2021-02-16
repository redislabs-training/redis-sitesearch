import time

import pytest


def test_no_content(client):
    result = client.simulate_get('/health')
    assert result.status_code == 503


def test_with_content(docs, client):
    result = client.simulate_get('/health')
    assert result.status_code == 200
