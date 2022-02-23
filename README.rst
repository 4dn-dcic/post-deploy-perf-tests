######################
post-deploy-perf-tests
######################

A collection of tests to be run to assess performance on a given FF/CGAP environment

^^^^^^^^^^
How To Run
^^^^^^^^^^

To run this, set LOCUST_USER, LOCUST_PASS, LOCUST_HOST in your env via test_cred.sh.
For CGAP: LOCUST_USER_CGAP, LOCUST_PASS_CGAP, LOCUST_HOST

Trigger a build through GA manually, or run locust locally to get very fine grained control and also get access to their UI which has some nice charts on it. It also allows you to download the test data. See the Makefile and locust docs on how Locust is invoked here.

To run locally with UI: ``make deploy-test-ui-ff``

To run in headless mode (same mode triggered by Travis): ``make deploy-test-headless-ff``

Replace "ff" with "cgap" to test on CGAP.
