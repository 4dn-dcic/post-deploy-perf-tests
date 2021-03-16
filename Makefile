configure:
	pip install poetry

build:
	poetry install

update:
	poetry update

test:
	python -m unittest lib.test.test_locust_api

deploy-test-ui-ff:
	python main.py fourfront

deploy-test-headless-ff:
	poetry run python main.py fourfront --headless

deploy-test-ui-cgap:
	python main.py cgap

deploy-test-headless-cgap:
	poetry run python main.py cgap --headless
