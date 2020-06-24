######################
post-deploy-perf-tests
######################

A collection of tests to be run to assess performance on a given FF environment

^^^^^^^^^^
How To Run
^^^^^^^^^^

Trigger a build manually, or run locust locally to get very fine grained control and also get access to their UI which has some nice charts on it. It also allows you to download the test data. See the Makefile and locust docs on how Locust is invoked here.

To run locally with UI: ``make deploy-test-ui``

To run in headless mode (same mode triggered by Travis): ``make deploy-test-headless``

^^^^^
TODOs
^^^^^

* Configure for CGAP.
* Do smarter things with routes (web crawling?).