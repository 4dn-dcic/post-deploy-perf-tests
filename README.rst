######################
post-deploy-perf-tests
######################

A collection of tests to be run to assess performance on a given FF/CGAP environment

^^^^^^^^^^
How To Run
^^^^^^^^^^

Trigger a build through Travis manually, or run locust locally to get very fine grained control and also get access to their UI which has some nice charts on it. It also allows you to download the test data. See the Makefile and locust docs on how Locust is invoked here.

To run locally with UI: ``make deploy-test-ui-ff``

To run in headless mode (same mode triggered by Travis): ``make deploy-test-headless-ff``

Replace "ff" with "cgap" to test on CGAP.

^^^^^
TODOs
^^^^^

* Configure NavigationUser for CGAP when more routes are available.
* Get more searches for CGAP.