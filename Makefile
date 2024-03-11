.PHONY: start dev check

start:
	pip install poetry
	poetry install
	pre-commit install

dev:
	poetry install -E "all"

check:
	pre-commit run --all-files
