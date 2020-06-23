configure:
	pip install poetry

build:
	poetry install

update:
	poetry update

test:
	python -m unittest lib.test.test_locust_api

deploy-test:
	echo "Enable the below test when access key is configured!"
	# locust -f deploy_tests/fourfront/fourfront.py --no-web -c 100 -r 10 --run-time 60s --print-stats
