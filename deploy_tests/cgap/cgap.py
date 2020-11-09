import json
import random
import requests
from requests.auth import HTTPBasicAuth
from locust import HttpUser, task, between
from lib.locust_api import LocustAuthHandler
from deploy_tests.utils import build_url


HOST = 'http://fourfront-cgapdev.9wzadzju3p.us-east-1.elasticbeanstalk.com'


# The following item types give no search result and thus 404, so we will not access their collection pages
BAD_ITEM_TYPES = ['AnnotationField', 'EvidenceDisPheno', 'GeneAnnotationField', 'Image', 'QualityMetricPeddyqc',
                  'QualityMetricWgsBamqc', 'TrackingItem', 'WorkflowMapping', 'WorkflowRun']


# Configuration
# 2 User configurations with possible 3rd extension later
#   * BasicUser - randomly navigate cases
#   * SearchUser - randomly execute searches
#   * NavigationUser - TODO: randomly navigate pages when we have more of them


class BasicUser(HttpUser):
    """ Locust user who will randomly get a case, spending 5-10 seconds on the page """
    host = HOST
    weight = 1
    wait_time = between(5, 10)
    _auth = HTTPBasicAuth(*LocustAuthHandler(is_ff=False).get_username_and_password())  # get CGAP auth
    cases = list(c['@id'] for c in requests.get(build_url(host, "/Case"), auth=_auth).json()['@graph'])
    item_types = list(t for t in requests.get(build_url(host, "/counts?format=json")).json()['db_es_compare'].keys()
                      if t not in BAD_ITEM_TYPES)

    @task(1)
    def get_case(self):
        """ Does a get for a random case """
        c = random.choice(self.cases)
        self.client.get(build_url(self.host, '%s' % c), auth=self._auth)

    @task(1)
    def get_collection(self):
        """ Gets collection views (searches) for all item types except those denoted as "bad" above. """
        t = random.choice(self.item_types)
        self.client.get(build_url(self.host, '/%s' % t), auth=self._auth)


class SearchUser(HttpUser):
    """ Locust user who will do lots of searches, some involving nested. """
    host = HOST
    weight = 1
    wait_time = between(1, 3)  # more frequent than BasicUser, so this will account for most of traffic
    _auth = HTTPBasicAuth(*LocustAuthHandler(is_ff=False).get_username_and_password())
    searches = json.load(open('./deploy_tests/cgap/searches.json', 'r'))['searches']

    @task(1)
    def get_search(self):
        """ Does a random search """
        route = build_url(self.host, random.choice(self.searches))
        self.client.get(route, auth=self._auth)


# class NavigationUser(HttpUser):
#     """ Navigation User for CGAP """
#     pass  # TODO: implement me!
