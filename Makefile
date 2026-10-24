PROJECT := $(notdir $(CURDIR))
VENV ?= $(HOME)/.venvs/$(PROJECT)

PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PREK := $(VENV)/bin/prek

.PHONY: setup check test run clean

setup:
	python3.13 -m venv $(VENV)
	$(PIP) install -e ".[dev]"
	$(PREK) install

check:
	$(PREK) run --all-files

test:
	$(PYTHON) -m pytest

run:
	$(PYTHON) -m spotify_utils.main

clean:
	rm -rf build dist src/*.egg-info *.egg-info
