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

    result = await client.get('/search?q=v6.0.20&site=https://docs.redislabs.com/latest/')
    assert "<b>v6</b>.0.20" in result.json()['results'][0]['body']

    result = await client.get('/search?q=v6.0.12&site=https://docs.redislabs.com/latest/')
    assert "<b>v6</b>.0.12" in result.json()['results'][0]['body']

    result = await client.get('/search?q=v6.0.8&site=https://docs.redislabs.com/latest/')
    assert "<b>v6</b>.0.8" in result.json()['results'][0]['body']

    result = await client.get('/search?q=v6.0&site=https://docs.redislabs.com/latest/')
    assert "<b>v6</b>.0" in result.json()['results'][0]['body']

    result = await client.get('/search?q=v5.6.0&site=https://docs.redislabs.com/latest/')
    assert "<b>v5</b>.6.0" in result.json()['results'][0]['body']

    result = await client.get('/search?q=v5.4.14&site=https://docs.redislabs.com/latest/')
    assert "<b>v5</b>.4.14" in result.json()['results'][0]['body']

    result = await client.get('/search?q=v5.4.10&site=https://docs.redislabs.com/latest/')
    assert "<b>v5</b>.4.10" in result.json()['results'][0]['body']

    result = await client.get('/search?q=v5.4.6&site=https://docs.redislabs.com/latest/')
    assert "<b>v5</b>.4.6" in result.json()['results'][0]['body']

    result = await client.get('/search?q=v5.4.4&site=https://docs.redislabs.com/latest/')
    assert "<b>v5</b>.4.4" in result.json()['results'][0]['body']

    result = await client.get('/search?q=v5.4.2&site=https://docs.redislabs.com/latest/')
    assert "<b>v5</b>.4.2" in result.json()['results'][0]['body']

    result = await client.get('/search?q=v5.4&site=https://docs.redislabs.com/latest/')
    assert "<b>v5</b>.4" in result.json()['results'][0]['body']
