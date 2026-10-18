.PHONY: setup

setup:
	python3.13 -m venv .venv
	.venv/bin/pip install -e ".[dev]"
	.venv/bin/prek install


check:
	.venv/bin/prek run --all-files
