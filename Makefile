.PHONY: start git check format clean

path = $(subst /,$(strip $(PATHSEP)),$1)

ifeq ($(OS),Windows_NT)
    RM = cmd.exe /C del /F /Q
    RMDIR = cmd.exe /C rd /S /Q
    PATHSEP = \\
    PIPINSTALL = cmd.exe /C "FOR %%i in (dist\*.whl) DO uv tool run poetry run python -m pip install --no-index --no-deps %%i"
    UVINSTALL = powershell -ExecutionPolicy ByPass -c "irm 'https://astral.sh/uv/install.ps1' | iex"
    CLEAN_PYCACHE = for /d /r . %%d in (__pycache__) do @(if exist "%%d" (rd /s /q "%%d"))
    CLEAN_PYTESTCACHE = for /d /r . %%d in (.pytest_cache) do @(if exist "%%d" (rd /s /q "%%d"))
    CLEAN_MYPYCACHE = for /d /r . %%d in (.mypy_cache) do @(if exist "%%d" (rd /s /q "%%d"))
else
    UNAME_S := $(shell uname -s 2>/dev/null || echo "unknown")
    ifeq ($(UNAME_S),Linux)
        RM = rm -f
        RMDIR = rm -rf
        PATHSEP = /
        PIPINSTALL = uv tool run poetry run python -m pip install dist/*.tar.gz
        UVINSTALL = curl -LsSf https://astral.sh/uv/install.sh | sh
        CLEAN_PYCACHE = find . -type d -name '__pycache__' -print0 | xargs -0 rm -rf
        CLEAN_PYTESTCACHE = find . -type d -name '.pytest_cache' -print0 | xargs -0 rm -rf
        CLEAN_MYPYCACHE = find . -type d -name '.mypy_cache' -print0 | xargs -0 rm -rf
    endif
    ifeq ($(UNAME_S),Darwin)
        RM = rm -f
        RMDIR = rm -rf
        PATHSEP = /
        PIPINSTALL = uv tool run poetry run python -m pip install dist/*.tar.gz
        UVINSTALL = curl -LsSf https://astral.sh/uv/install.sh | sh
        CLEAN_PYCACHE = find . -type d -name '__pycache__' -print0 | xargs -0 rm -rf
        CLEAN_PYTESTCACHE = find . -type d -name '.pytest_cache' -print0 | xargs -0 rm -rf
        CLEAN_MYPYCACHE = find . -type d -name '.mypy_cache' -print0 | xargs -0 rm -rf
    endif
endif

start:
	$(UVINSTALL)
	uv python install 3.9.20
	uv tool install poetry==2.1.1
	uv tool run poetry config virtualenvs.in-project true
	uv tool run poetry self add poetry-bumpversion
	uv tool run poetry env use $(shell uv python find 3.9.20)
	uv tool run poetry install
	uv tool run poetry run pre-commit install

git:
	git config --global core.eol lf
	git config --global core.autocrlf input
	git config --global core.safecrlf true
	git config --global http.proxy http://127.0.0.1:7897
	git config --global https.proxy http://127.0.0.1:7897

check:
	- uv tool run poetry run pre-commit run --all-files
	- uv tool run poetry run ruff check --fix

format:
	- uv tool run poetry run ruff format
	- uv tool run poetry run ruff check --fix

clean:
	-$(CLEAN_PYCACHE)
	-$(CLEAN_PYTESTCACHE)
	-$(CLEAN_MYPYCACHE)
	-$(RMDIR) $(call path, dist)
	-$(RMDIR) $(call path, file.log)
	-$(RMDIR) $(call path, docs$(PATHSEP)_build)
	-$(RMDIR) $(call path, htmlcov)
	-$(RM) $(call path, .coverage)
	-$(RM) $(call path, .coverage.*)
	-$(RM) $(call path, coverage.xml)
	-$(RMDIR) $(call path, .tox)
	-$(RMDIR) $(call path, uv_demo.egg-info)
