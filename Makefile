export PIPENV_VERBOSITY=-1

# Dev utilities
dev:
	make deps
	bin/dc up -d

deps:
	make venv
	make docker_build
	make generate
	make frontend_deps

frontend_deps:
	cd hotbot/views && yarn

docker_build:
	bin/dc build

docker_build_clean:
	bin/dc build --no-cache

generate:
	python3 hotbot/cli.py generate-enums

format:
	make ruff_format
	make mypy

venv:
	uv venv .venv
	uv pip install -e .

freeze:
	uv pip freeze | grep -v hotbot > requirements.freeze.txt

precommit:
	make format
	make generate
	make test
	make freeze

# CI Pipeline & Tests

test:
	pytest

test_backend_coverage:
	pytest --cov=hotbot/apps --cov-config=.coveragerc --cov-report html --cov-report term
	echo "View coverage report: file://${PWD}/htmlcov/index.html"

# Data management & Backups
dump_fixtures:
	bin/djmanage dumpdata --natural-primary --natural-foreign --format json --indent 2 users

# Codebase Linting & Cleanup

clean:
	find . -name '*.pyc' -delete

mypy:
	mypy

autoflake:
	autoflake -r -i --expand-star-imports --remove-all-unused-imports --remove-duplicate-keys --remove-unused-variables --ignore-init-module-imports hotbot/apps/

ruff_check:
	ruff check .

ruff_format:
	ruff format .
