from async_asgi_testclient import TestClient
from src.source1 import app as source1_app
from src.source2 import app as source2_app
from src.source3 import app as source3_app
import pytest
import json


@pytest.fixture()
def source_apps():
    apps = {
        'bitcoin': source1_app,
        'tinkoff': source2_app,
        'meta': source3_app
    }
    return apps


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
async def test_answer(source_apps):
    max_lines = 5
    i = 0
    for stock, app in source_apps.items():
        async with TestClient(app) as client:
            resp = await client.get(f"/{stock}/price", stream=True)
            assert resp.status_code == 200
            async for line in resp:
                if i > max_lines:
                    break
                res = decode_line(line.decode('utf-8').strip())
                assert res['event'] == "price_change"
                assert res['data']['stock'] == stock
                i += 1
