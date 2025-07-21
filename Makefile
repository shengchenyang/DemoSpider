.PHONY: start git dev check

start:
	pyenv local 3.9.20
	pip install poetry==2.1.1
	poetry config virtualenvs.in-project true
	poetry env use python
	poetry install
	poetry run pre-commit install

git:
	git config --global core.eol lf
	git config --global core.autocrlf input
	git config --global core.safecrlf true
	git config --global http.proxy http://127.0.0.1:7897
	git config --global https.proxy http://127.0.0.1:7897

dev:
	poetry install

check:
	pre-commit run --all-files
