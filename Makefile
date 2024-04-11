VENV=venv
PYTHON=$(VENV)/bin/python3

venv:
	python -m venv $(VENV)

install: venv
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest tests/test_bots.py tests/test_sources.py
	$(PYTHON) -m pytest tests/test_market.py

start:
	$(PYTHON) src/source1.py &
	$(PYTHON) src/source2.py &
	$(PYTHON) src/source3.py &
	$(PYTHON) src/market.py &
	$(PYTHON) src/bot_investor.py &
	$(PYTHON) src/bot_hamster.py &
