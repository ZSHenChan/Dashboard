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

# The 'run' target now depends on the 'install' target
run: install
	poetry run python app/main.py --env $(ENV) $(DEBUG_FLAG)

# Target to install dependencies
install:
	poetry install

help:
	@echo "Usage: make run ENV=local|dev|prod DEBUG=true|false"