import json
import random
import requests
from requests.auth import HTTPBasicAuth
from locust import HttpUser, task, between
from lib.locust_api import LocustAuthHandler
from deploy_tests.utils import build_url


# TODO: make arg
#HOST = 'https://cgap-msa.hms.harvard.edu'
HOST = 'https://cgap-devtest.hms.harvard.edu'


# Configuration
# 2 User configurations with possible 3rd extension later
#   * BasicUser - randomly navigate cases
#   * SearchUser - randomly execute searches in paginated ranges

#
class BasicUser(HttpUser):
    """ Locust user who will randomly get a case, spending 5-10 seconds on the page """
    host = HOST
    weight = 1
    wait_time = between(3, 5)
    _auth = HTTPBasicAuth(*LocustAuthHandler(is_ff=False).get_username_and_password())  # get CGAP auth
    cases = list(c['@id'] for c in requests.get(build_url(host, "/Case?limit=10"), auth=_auth).json()['@graph'])
    # These types are most data model intensive
    item_types = ['Case', 'Variant', 'VariantSample', 'FileProcessed', 'File', 'QualityMetric',
                  'MetaWorkflow', 'MetaWorkflowRun']

    @task(1)
    def get_case(self):
        """ Does a get for a random case """
        c = random.choice(self.cases)
        self.client.get(build_url(self.host, '%s' % c), auth=self._auth)

    @task(4)
    def get_collection(self):
        """ Gets collection views (searches) for all item types except those denoted as "bad" above. """
        t = random.choice(self.item_types)
        self.client.get(build_url(self.host, '/%s' % t), auth=self._auth)


# TODO: re-enable once more search data is available
class SearchUser(HttpUser):
    """ Locust user who will do lots of searches, some involving nested. """
    pagination_depth = 30  # limit depth - adjust this value accordingly
    host = HOST
    weight = 1
    wait_time = between(4, 8)  # Normal user actually is more representative (case navigation) so make these even
    _auth = HTTPBasicAuth(*LocustAuthHandler(is_ff=False).get_username_and_password())
    counts = requests.get(build_url(host, "/counts?format=json")).json()['db_es_compare']
    searches = []
    for t, counts in counts.items():
        # example value of split totals: ['DB:', '74048', 'ES:', '74048']
        # or ['DB:', '887', 'ES:', '888', '<', 'ES', 'has', '1', 'more', 'items', '>']
        parsed_counts = int(counts.split()[3])  # es_total
        if parsed_counts > pagination_depth:
            parsed_counts = pagination_depth
        # skip types
        if t not in ['Case', 'Variant', 'VariantSample', 'FileFastq', 'File', 'QualityMetric', 'MetaWorkflow', 'MetaWorkflowRun']:
            continue
        for page in range(0, parsed_counts, 10):  # paginate with size=10
            searches.append(f'/{t}/?from={page}&limit=10')

    @task(1)
    def get_search(self):
        """ Does a random search """
        route = build_url(self.host, random.choice(self.searches))
        self.client.get(route, auth=self._auth)
