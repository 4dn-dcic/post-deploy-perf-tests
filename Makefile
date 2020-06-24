configure:
	pip install poetry

build:
	poetry install

update:
	poetry update

test:
	python -m unittest lib.test.test_locust_api

deploy-test-ui:
	python main.py fourfront

deploy-test-headless:
	python main.py fourfront --headless
