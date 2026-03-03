# Default values
ENV ?= local
DEBUG ?= true

# Formatting logic for the debug flag
ifeq ($(DEBUG), true)
    DEBUG_FLAG := --debug
else
    DEBUG_FLAG :=
endif

.PHONY: run install help

dev:
	PYTHONPATH=. poetry run python app/main.py --env $(ENV) $(DEBUG_FLAG)

install:
	poetry install

test:
	poetry run pytest tests/ --cov=src

lint:
	poetry run ruff check .

build-image:
	docker build -t myapp:latest .

run-container:
	docker run -p 8000:8000 myapp:latest

help:
	@echo "Usage: make run ENV=local|dev|prod DEBUG=true|false"