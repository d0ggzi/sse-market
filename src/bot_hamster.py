import logging
import time

import requests
from sseclient import SSEClient
import json
from .settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
log_format = (
    "%(filename)s \t %(asctime)s \t " "%(levelname)s \t %(message)s \t %(funcName)s"
)
handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(handler)

INTERESTED_IN = {'meta', 'tinkoff'}
prev_price = {el: [0.0, 0.0, 0.0] for el in INTERESTED_IN}
bought_price = {el: 0 for el in INTERESTED_IN}


def send_to_market(url, stock):
    request_options = {
        "username": "hamster1",
        "stock": stock,
        "amount": 1 if stock == 'bitcoin' else 5
    }

    requests.post(url, data=json.dumps(request_options))


def check_price():
    for stock, prices in prev_price.items():
        if prices[0] < prices[1] > prices[2]:
            bought_price[stock] = max(bought_price[stock], prices[2])
            logger.info(f"Buying <{stock}> for {prices[2]}")
            send_to_market(f'http://{settings.MARKET_HOST}:{settings.MARKET_PORT}/buy', stock)
        elif prices[0] > prices[1] < prices[2] and bought_price[stock] > prices[2]:
            logger.info(f"Selling <{stock}> for {prices[2]}")
            bought_price[stock] = 0
            send_to_market(f'http://{settings.MARKET_HOST}:{settings.MARKET_PORT}/sell', stock)


def get_messages(messages):
    for msg in messages:
        if msg.data:
            msg = json.loads(msg.data.replace("'", "\""))
            for stock, price in msg.items():
                if stock in prev_price:
                    prev_price[stock].pop(0)
                    prev_price[stock].append(float(price))
            check_price()


if __name__ == "__main__":
    while True:
        # in case market is not working currently
        try:
            messages = SSEClient(f'http://{settings.MARKET_HOST}:{settings.MARKET_PORT}/api/prices')
            get_messages(messages)
        except requests.exceptions.ConnectionError as e:
            logger.info("Trying to connect to market. Please, wait...")
            time.sleep(5)
