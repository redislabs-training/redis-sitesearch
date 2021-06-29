import pytest


@pytest.mark.asyncio
async def test_query_python(docs, client):
    result = await client.get('/search?q=*')
    assert result.status_code == 200
    assert result.json()['total'] > 0
    titles = [doc['title'] for doc in result.json()['results']]
    assert 'Database Persistence with Redis Enterprise Software' in titles


@pytest.mark.asyncio
async def test_cloud_landing_page(client):
    result = await client.get('/search?q=cloud')
    assert result.json()['results'][0]['title'] == 'Redis Enterprise Cloud'
    assert result.json()['results'][0]['url'] == 'https://docs.redislabs.com/latest/rc/'


@pytest.mark.asyncio
async def test_escapes_good_symbols(docs, client):
    result = await client.get('/search?q=active-active')
    assert "<b>Active</b>-Active" in result.json()['results'][0]['title']
