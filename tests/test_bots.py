from unittest.mock import Mock

from src import bot_investor, bot_hamster
from src.settings import settings
import requests
from sseclient import Event


def test_investor_buying():
    events = [
        Event(data='{"bitcoin": "70400", "tinkoff": "33.95", "meta": "505.47"}', event='price_changes'),
        Event(data='{"bitcoin": "70000", "tinkoff": "33.95", "meta": "505.47"}', event='price_changes'),
        Event(data='{"bitcoin": "70100", "tinkoff": "33.95", "meta": "505.47"}', event='price_changes')
    ]

    requests.post = Mock()
    bot_investor.get_messages(events)
    requests.post.assert_called_with(f'http://{settings.MARKET_HOST}:{settings.MARKET_PORT}/buy',
                                     data='{"username": "investor228", "stock": "bitcoin", "amount": 1}')


def test_investor_selling():
    events = [
        Event(data='{"bitcoin": "70400", "tinkoff": "33.95", "meta": "505.47"}', event='price_changes'),
        Event(data='{"bitcoin": "70000", "tinkoff": "33.95", "meta": "505.47"}', event='price_changes'),
        Event(data='{"bitcoin": "70100", "tinkoff": "33.95", "meta": "505.47"}', event='price_changes'),
        Event(data='{"bitcoin": "70500", "tinkoff": "33.95", "meta": "505.47"}', event='price_changes'),
        Event(data='{"bitcoin": "70490", "tinkoff": "33.95", "meta": "505.47"}', event='price_changes')
    ]

    requests.post = Mock()
    bot_investor.get_messages(events)
    requests.post.assert_called_with(f'http://{settings.MARKET_HOST}:{settings.MARKET_PORT}/sell',
                                     data='{"username": "investor228", "stock": "bitcoin", "amount": 1}')


def test_hamster_buying():
    events = [
        Event(data='{"bitcoin": "70400", "tinkoff": "33.95", "meta": "505.47"}', event='price_changes'),
        Event(data='{"bitcoin": "70400", "tinkoff": "34.95", "meta": "505.47"}', event='price_changes'),
        Event(data='{"bitcoin": "70400", "tinkoff": "34.85", "meta": "505.47"}', event='price_changes')
    ]

    requests.post = Mock()
    bot_hamster.get_messages(events)
    requests.post.assert_called_with(f'http://{settings.MARKET_HOST}:{settings.MARKET_PORT}/buy',
                                     data='{"username": "hamster1", "stock": "tinkoff", "amount": 5}')


def test_hamster_selling():
    events = [
        Event(data='{"bitcoin": "70400", "tinkoff": "33.95", "meta": "505.47"}', event='price_changes'),
        Event(data='{"bitcoin": "70000", "tinkoff": "34.95", "meta": "505.47"}', event='price_changes'),
        Event(data='{"bitcoin": "70100", "tinkoff": "33.85", "meta": "505.47"}', event='price_changes'),
        Event(data='{"bitcoin": "70500", "tinkoff": "33.55", "meta": "505.47"}', event='price_changes'),
        Event(data='{"bitcoin": "70490", "tinkoff": "33.65", "meta": "505.47"}', event='price_changes')
    ]

    requests.post = Mock()
    bot_hamster.get_messages(events)
    requests.post.assert_called_with(f'http://{settings.MARKET_HOST}:{settings.MARKET_PORT}/sell',
                                     data='{"username": "hamster1", "stock": "tinkoff", "amount": 5}')
