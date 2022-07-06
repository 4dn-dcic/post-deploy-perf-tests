import json
import random
import requests
from requests.auth import HTTPBasicAuth
from locust import HttpUser, task, between
from lib.locust_api import LocustAuthHandler, pdpt_get
from deploy_tests.utils import build_url


# The following item types give no search result and thus 404, so we will not access their collection pages
BAD_ITEM_TYPES = ['Target', 'SopMap', 'PublicationTracking', 'QualityMetricFlag', 'SummaryStatistic',
                  'QualityMetricBamcheck', 'SummaryStatisticHiC', 'ImageSetting']

# Configuration
# 3 different 'User' classifications, weighted equally:
#   * BasicUser - randomly moves from the index page to item collection views.
#   * NavigationUser - randomly moves between navigation bar pages
#   * SearchUser - randomly executes a search randomly selected from a source of real searches over several days


class BasicUser(HttpUser):
    """ Locust user who does basic things on the site at regular intervals. This involves a combination of generic page
        requests and search requests split 75-25. """
    locust_auth = LocustAuthHandler()
    host = locust_auth.host
    weight = 1  # adjust as needed
    wait_time = between(3, 5)
    _auth = HTTPBasicAuth(*locust_auth.get_username_and_password())
    item_types = list(t for t in requests.get(build_url(host, "/counts?format=json")).json()['db_es_compare'].keys()
                      if t not in BAD_ITEM_TYPES)

    @task(1)
    def index(self):
        """ Gets the main page - normal request + search AJAX requests """
        pdpt_get(client=self.client, url=build_url(self.host, '/'), auth=self._auth)

    @task(3)
    def search(self):
        """ Selects an item type on this portal at random and navigates to its browse page, which
            redirects to search. More lightweight than the index page WRT our application but could
            stress back-end resources.
        """
        t = random.choice(self.item_types)
        pdpt_get(client=self.client, url=build_url(self.host, '/%s' % t), auth=self._auth)


class NavigationUser(HttpUser):
    """ Locust user who "clicks" through all navigation bar links at a faster rate than the
        BasicUser. """
    locust_auth = LocustAuthHandler()
    host = locust_auth.host
    weight = 1  # adjust as needed
    wait_time = between(1, 3)
    _auth = HTTPBasicAuth(*locust_auth.get_username_and_password())
    data_pages = [
        '/browse/?experimentset_type=replicate&type=ExperimentSetReplicate',
        '/browse/?experimentset_type=replicate&type=ExperimentSetReplicate&experiments_in_set.experiment_type.experiment_category=Sequencing',
        '/microscopy-data-overview',
        '/search/?type=Publication&sort=static_content.location&sort=-number_of_experiment_sets&number_of_experiment_sets.from=1'
    ]
    tools_pages = [
        '/tools',
        '/tools/visualization',
        '/tools/jupyterhub'
    ]
    resources_pages = [
        '/resources/experimental-resources/cell-lines',
        '/resources/experimental-resources/experiment-types',
        '/resources/data-analysis/reproducible-data-analysis',
        '/resources/data-analysis/reference-files',
        '/resources/data-analysis/hi_c-processing-pipeline',
        '/resources/data-analysis/repli-seq-processing-pipeline',
        '/resources/data-analysis/chipseq-processing-pipeline',
        '/resources/data-analysis/atacseq-processing-pipeline',
        '/resources/data-analysis/rnaseq-processing-pipeline',
        '/resources/data-analysis/qc',
        '/joint-analysis',
        '/4DN-AICS-Collaboration',
        '/hic-data-overview'
    ]
    help_pages = [
        '/help/user-guide/getting-started',
        '/help/user-guide/data-model',
        '/help/user-guide/biosample-metadata',
        '/help/user-guide/rest-api',
        '/help/user-guide/account-creation',
        '/help/submitter-guide/getting-started-with-submissions',
        '/help/submitter-guide/spreadsheet-submission',
        '/help/submitter-guide/online-submission',
        '/help/submitter-guide/submitting_processed_results',
        '/help/about/about-dcic',
        '/help/about/privacy-policy'
    ]

    @task(1)
    def data_page(self):
        """ Accesses a random data page """
        route = build_url(self.host, random.choice(self.data_pages))
        pdpt_get(client=self.client, url=route, auth=self._auth)

    @task(1)
    def tools_page(self):
        """ Accesses a random tools page """
        route = build_url(self.host, random.choice(self.tools_pages))
        pdpt_get(client=self.client, url=route, auth=self._auth)

    @task(1)
    def resource_page(self):
        """ Accesses a random resource page """
        route = build_url(self.host, random.choice(self.tools_pages))
        pdpt_get(client=self.client, url=route, auth=self._auth)

    @task(1)
    def help_page(self):
        """ Accesses a random help page """
        route = build_url(self.host, random.choice(self.help_pages))
        pdpt_get(client=self.client, url=route, auth=self._auth)


class SearchUser(HttpUser):
    """ Locust user who does only search requests at a faster rate than both of the previous two.
        Searches are picked randomly from a sample of searches on production.
    """
    locust_auth = LocustAuthHandler()
    host = locust_auth.host
    weight = 1  # adjust as needed
    wait_time = between(1, 2)
    _auth = HTTPBasicAuth(*locust_auth.get_username_and_password())
    searches = json.load(open('./deploy_tests/fourfront/searches.json', 'r'))['searches']

    @task(1)
    def search(self):
        """ Does a random search """
        route = build_url(self.host, random.choice(self.searches))
        pdpt_get(client=self.client, url=route, auth=self._auth)
