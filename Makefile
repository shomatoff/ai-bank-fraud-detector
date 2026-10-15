PYTHON := .venv/bin/python

.PHONY: install train data test lint audit run
install:
	python3 -m venv .venv
	$(PYTHON) -m pip install -c constraints-verified.txt --upgrade pip
	$(PYTHON) -m pip install -c constraints-verified.txt -r requirements-dev.txt
train:
	$(PYTHON) -m fraud_detector.model
data:
	$(PYTHON) -m scripts.generate_data --rows 12000 --seed 42
test:
	$(PYTHON) -m pytest -q
lint:
	.venv/bin/ruff check fraud_detector tests scripts
audit:
	.venv/bin/pip-audit
run:
	.venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
