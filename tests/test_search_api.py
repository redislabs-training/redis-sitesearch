import pytest


@pytest.mark.asyncio
async def test_query_python(docs, client):
    result = await client.get('/search?q=*&site=https://docs.redislabs.com/latest/')
    assert result.status_code == 200
    assert result.json()['total'] > 0
    titles = [doc['title'] for doc in result.json()['results']]
    assert 'Database Persistence with Redis Enterprise Software' in titles


@pytest.mark.asyncio
async def test_cloud_landing_page(docs, client):
    result = await client.get('/search?q=cloud&site=https://docs.redislabs.com/latest/')
    assert result.json()['results'][0]['title'] == 'Redis Enterprise Cloud'
    assert result.json()['results'][0]['url'] == 'https://docs.redislabs.com/latest/rc/'


@pytest.mark.asyncio
async def test_escapes_good_symbols(docs, client):
    result = await client.get('/search?q=active-active&site=https://docs.redislabs.com/latest/')
    assert "<b>Active</b>-Active" in result.json()['results'][0]['title']


@pytest.mark.asyncio
async def test_escapes_known_version_numbers(docs, client):
    result = await client.get('/search?q=v6.2.8&site=https://docs.redislabs.com/latest/')
    assert "<b>v6</b>.2.8" in result.json()['results'][0]['body']
    
    result = await client.get('/search?q=v6.2.4&site=https://docs.redislabs.com/latest/')
    assert "<b>v6</b>.2.4" in result.json()['results'][0]['body']
