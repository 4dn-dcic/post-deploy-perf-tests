import json
import random
import requests
from requests.auth import HTTPBasicAuth
from locust import HttpUser, task, between
from lib.locust_api import LocustAuthHandler
from deploy_tests.utils import build_url


HOST = 'http://localhost:8000'


# The following item types give no search result and thus 404, so we will not access their collection pages
BAD_ITEM_TYPES = ['AnnotationField', 'GeneAnnotationField', 'Image', 'QualityMetricPeddyqc', 'TrackingItem',
                  'WorkflowMapping', 'WorkflowRun']


# might be useful?
CASE_INFO_EXTENSIONS = ['#case-info.accessioning', '#case-info.bioinformatics', '#case-info.filtering']


# temporary localhost credentials
_auth = ('testing-user', 'testing-password')


# Configuration
# 2 User configurations
#   * BasicUser - randomly navigate cases
#   * SearchUser - randomly execute searches


class BasicUser(HttpUser):
    """ Locust user who will randomly get a case, spending 5-10 seconds on the page """
    host = HOST
    weight = 1
    wait_time = between(5, 10)
    _auth = _auth  # HTTPBasicAuth(*LocustAuthHandler(is_ff=False).get_username_and_password())  # get CGAP auth
    cases = list(c['@id'] for c in requests.get(build_url(host, "/Case"), auth=_auth).json()['@graph'])

    @task(1)
    def case(self):
        """ Does a get for a random case """
        c = random.choice(self.cases)
        self.client.get(build_url(self.host, '%s' % c), auth=self._auth)


class SearchUser(HttpUser):
    """ Locust user who will do lots of searches, some involving nested. """
    host = HOST
    weight = 1
    wait_time = between(1, 3)  # more frequent than BasicUser, so this will account for most of traffic
    _auth = _auth  # HTTPBasicAuth(*LocustAuthHandler(is_ff=False).get_username_and_password())
    nested_searches = []
    standard_searches = []

    @task(1)
    def search(self):
        """ Does a random search """
        pass