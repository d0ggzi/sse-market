import asyncio
import sys
from contextlib import asynccontextmanager

import pydantic
from fastapi.exceptions import HTTPException

import uvicorn
from fastapi import FastAPI, Response
from sse_starlette import EventSourceResponse
from starlette.requests import Request
import logging
from sseclient import SSEClient
import json
from .settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
log_format = (
    "%(filename)s \t %(asctime)s \t " "%(levelname)s \t %(message)s \t %(funcName)s"
)
handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(handler)


current_price = dict()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # to mock it with pytest
    if "pytest" not in sys.modules:
        messages_btc = SSEClient('http://localhost:8081/bitcoin/price')
        messages_tkf = SSEClient('http://localhost:8082/tinkoff/price')
        messages_meta = SSEClient('http://localhost:8083/meta/price')

        loop = asyncio.get_event_loop()
        loop.create_task(get_messages(zip(messages_btc, messages_tkf, messages_meta)))

    yield


app = FastAPI(lifespan=lifespan)


async def get_messages(sources: zip):
    """get and parse messages from sources"""
    for msgs in sources:
        for msg in msgs:
            if msg.data:
                msg = json.loads(msg.data.replace("'", "\""))
                current_price[msg['stock']] = msg['price']
        logger.debug(f"The current price is {current_price}")
        await asyncio.sleep(settings.DELAY_SECONDS)


class Info(pydantic.BaseModel):
    username: str
    stock: str
    amount: int


@app.post("/buy")
async def buy_stock(info: Info):
    if info.stock not in current_price:
        raise HTTPException(status_code=404, detail="No such stock")
    logger.info(
        f"User @{info.username} is buying stock <{info.stock}> in amount of {info.amount} for {current_price[info.stock]}")
    return Response(status_code=200)


@app.post("/sell")
async def sell_stock(info: Info):
    if info.stock not in current_price:
        raise HTTPException(status_code=404, detail="No such stock")
    logger.info(
        f"User @{info.username} is selling stock <{info.stock}> in amount of {info.amount} for {current_price[info.stock]}")
    return Response(status_code=200)


@app.get("/api/prices")
async def message_stream(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                print("Request disconnected")
                break

            yield {
                "event": "price_changes",
                "data": current_price
            }

            await asyncio.sleep(settings.DELAY_SECONDS)

    return EventSourceResponse(event_generator())


if __name__ == '__main__':
    uvicorn.run(app, host=settings.MARKET_HOST, port=settings.MARKET_PORT)
