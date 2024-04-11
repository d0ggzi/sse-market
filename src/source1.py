import asyncio
import uvicorn
import random
from fastapi import FastAPI
from sse_starlette import EventSourceResponse
from starlette.requests import Request
import logging

from .settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
log_format = (
    "%(filename)s \t %(asctime)s \t " "%(levelname)s \t %(message)s \t %(funcName)s"
)
handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(handler)

app = FastAPI()

BITCOIN_PRICE = 70400


@app.get("/bitcoin/price")
async def message_stream(request: Request):
    async def event_generator():
        up_down = 1
        cur_price = BITCOIN_PRICE
        while True:
            if await request.is_disconnected():
                logger.info("Request disconnected")
                break
            cur_price = round(cur_price - random.randint(0, 10) * up_down, 2)
            logger.info(f"Current price of bitcoin is {cur_price}")
            yield {
                "event": "price_change",
                "data": {
                    "stock": "bitcoin",
                    "price": cur_price
                },
            }
            if random.choices([True, False], [0.15, 0.85])[0]:
                up_down = -up_down

            await asyncio.sleep(settings.DELAY_SECONDS)

    return EventSourceResponse(event_generator())


if __name__ == '__main__':
    uvicorn.run(app, host=settings.SOURCE1_HOST, port=settings.SOURCE1_PORT)
