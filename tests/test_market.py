from fastapi.testclient import TestClient
from async_asgi_testclient import TestClient as AsyncTestClient
from sseclient import Event
from src.market import get_messages, current_price, app
import pytest
import json


@pytest.fixture()
def sources():
    source1 = [Event(data='{"stock": "bitcoin", "price": 70400}', event='price_changes')]
    source2 = [Event(data='{"stock": "tinkoff", "price": 33.95}', event='price_changes')]
    source3 = [Event(data='{"stock": "meta", "price": 505.47}', event='price_changes')]

    return zip(source1, source2, source3)


def decode_line(line: str) -> dict:
    lines = line.split("\n")
    result = dict()
    for el in lines:
        key, value = map(str.strip, el.split(":", 1))
        if key == 'data':
            value = value.replace("'", '"')
            value = json.loads(value)
        result[key] = value
    return result


@pytest.mark.asyncio
async def test_prices(sources):
    await get_messages(sources)
    assert current_price['bitcoin'] == 70400
    assert current_price['tinkoff'] == 33.95


@pytest.mark.asyncio
async def test_buy_stock_bad(sources):
    await get_messages(sources)
    request_options = {
        "username": "testing",
        "stock": "test",
        "amount": 3
    }
    with TestClient(app) as client:
        resp = client.post("/buy", json=request_options)
        assert resp.status_code == 404
        assert resp.json() == {"detail": "No such stock"}


@pytest.mark.asyncio
async def test_buy_stock_well(sources):
    await get_messages(sources)
    request_options = {
        "username": "testing",
        "stock": "bitcoin",
        "amount": 1
    }
    with TestClient(app) as client:
        resp = client.post("/buy", json=request_options)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_sell_stock_well(sources):
    await get_messages(sources)
    request_options = {
        "username": "testing",
        "stock": "bitcoin",
        "amount": 1
    }
    with TestClient(app) as client:
        resp = client.post("/sell", json=request_options)
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_sell_stock_bad(sources):
    await get_messages(sources)
    request_options = {
        "username": "testing",
        "stock": "test",
        "amount": 3
    }
    with TestClient(app) as client:
        resp = client.post("/sell", json=request_options)
        assert resp.status_code == 404
        assert resp.json() == {"detail": "No such stock"}


@pytest.mark.asyncio
async def test_answer(sources):
    await get_messages(sources)
    # sources = sources.__next__()
    # requests_mock.get('http://localhost:8081/bitcoin/price', text=sources[0].__str__())
    # requests_mock.get('http://localhost:8082/tinkoff/price', text=sources[1].__str__())
    # requests_mock.get('http://localhost:8083/meta/price', text=sources[2].__str__())
    max_lines = 3
    i = 0

    async with AsyncTestClient(app) as client:
        resp = await client.get(f"/api/prices", stream=True)
        assert resp.status_code == 200
        async for line in resp:
            if i > max_lines:
                break
            res = decode_line(line.decode('utf-8').strip())
            assert res['event'] == "price_changes"
            assert res['data']['bitcoin'] == 70400
            assert res['data']['tinkoff'] == 33.95
            assert res['data']['meta'] == 505.47
            i += 1