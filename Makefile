configure:
	pip install poetry

build:
	poetry install

update:
	poetry update

test:
    python -m unittest lib.test.test_locust_api
