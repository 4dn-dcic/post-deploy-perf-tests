import json
import random
import requests
from requests.auth import HTTPBasicAuth
from locust import HttpUser, task, between
from lib.locust_api import LocustAuthHandler
from deploy_tests.utils import build_url


# Configuration
# 2 User configurations with possible 3rd extension later
#   * BasicUser - randomly navigate cases
#   * SearchUser - randomly execute searches in paginated ranges

#
class BasicUser(HttpUser):
    """ Locust user who will randomly get a case, spending 5-10 seconds on the page """
    locust_auth = LocustAuthHandler(is_ff=False)
    host = locust_auth.host
    weight = 1
    wait_time = between(3, 5)
    _auth = HTTPBasicAuth(*locust_auth.get_username_and_password())  # get CGAP auth
    requests.get(build_url(host, "/Case?limit=20"), auth=_auth).json()
    cases = list(c['@id'] for c in requests.get(build_url(host, "/Case?limit=20"), auth=_auth).json()['@graph'])
    vsl = list(c['@id'] for c in requests.get(build_url(host, '/VariantSampleList?limit=10'), auth=_auth).json()['@graph'])
    # These types are most data model intensive
    item_types = ['Case', 'Variant', 'VariantSample', 'FileProcessed', 'File', 'QualityMetric',
                  'MetaWorkflow', 'MetaWorkflowRun']

    @task(8)
    def get_case(self):
        """ Does a get for a random case """
        c = random.choice(self.cases)
        self.client.get(build_url(self.host, '%s' % c), auth=self._auth)

    # enable this to get info about VSL, but not an expensive API
    #@task(1)
    def get_vsl(self):
        """ Does a get for a random variant sample list (intepretation space) """
        c = random.choice(self.vsl)
        self.client.get(build_url(self.host, '%s' % c), auth=self._auth)


class SearchUser(HttpUser):
    """ Locust user who will do lots of searches, some involving nested. """
    pagination_depth = 30  # limit depth - adjust this value accordingly
    locust_auth = LocustAuthHandler(is_ff=False)
    host = locust_auth.host
    weight = 3
    wait_time = between(4, 8)  # Normal user actually is more representative (case navigation) so make these even
    _auth = HTTPBasicAuth(*locust_auth.get_username_and_password())
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
