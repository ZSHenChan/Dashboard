# Default values
ENV ?= dev
DEBUG ?= true

# Formatting logic for the debug flag
ifeq ($(DEBUG), true)
    DEBUG_FLAG := --debug
else
    DEBUG_FLAG := 
endif

.PHONY: run install help

# The 'run' target now depends on the 'install' target
install:
	poetry install

run: install
	poetry run python main.py --env $(ENV) $(DEBUG_FLAG)

help:
	@echo "Usage: make run ENV=local|dev|prod DEBUG=true|false"