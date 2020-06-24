import json
import random
import requests
from requests.auth import HTTPBasicAuth
from locust import HttpUser, task, between
from lib.locust_api import LocustAuthHandler


HOST = 'http://staging.4dnucleome.org'  # We run performance tests on staging


def build_url(base, postfix):
    """ Combines base + postfix to build a full url

    :param base: base url ie: https://data.4dnucleome.org/
    :param postfix: postfix to add, such as /search/?type=Item
    :return: a full url
    """
    return base + postfix


# The following item types give no search result and thus 404, so we will not access their collection pages
BAD_ITEM_TYPES = ['Target', 'SopMap', 'PublicationTracking', 'QualityMetricFlag', 'SummaryStatistic',
                  'QualityMetricBamcheck', 'SummaryStatisticHiC']


class BasicUser(HttpUser):
    """ Locust user who does basic things on the site at regular intervals. This involves a combination of generic page
        requests and search requests split 75-25. """
    host = HOST
    weight = 1  # adjust as needed
    wait_time = between(3, 5)
    _auth = HTTPBasicAuth(*LocustAuthHandler().get_username_and_password())
    item_types = list(t for t in requests.get(build_url(host, "/counts?format=json")).json()['db_es_compare'].keys()
                      if t not in BAD_ITEM_TYPES)

    @task(1)
    def index(self):
        """ Gets the main page - normal request + search AJAX requests """
        self.client.get(build_url(self.host, '/'), auth=self._auth)

    @task(3)
    def search(self):
        """ Selects an item type on this portal at random and navigates to its browse page, which
            redirects to search. More lightweight than the index page WRT our application but could
            stress back-end resources.
        """
        t = random.choice(self.item_types)
        self.client.get(build_url(self.host, '/%s' % t), auth=self._auth)


class NavigationUser(HttpUser):
    """ Locust user who "clicks" through all navigation bar links at a faster rate than the
        BasicUser. """
    host = HOST
    weight = 1  # adjust as needed
    wait_time = between(1, 3)
    _auth = HTTPBasicAuth(*LocustAuthHandler().get_username_and_password())
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
        self.client.get(route, auth=self._auth)

    @task(1)
    def tools_page(self):
        """ Accesses a random tools page """
        route = build_url(self.host, random.choice(self.tools_pages))
        self.client.get(route, auth=self._auth)

    @task(1)
    def resource_page(self):
        """ Accesses a random resource page """
        route = build_url(self.host, random.choice(self.tools_pages))
        self.client.get(route, auth=self._auth)

    @task(1)
    def help_page(self):
        """ Accesses a random help page """
        route = build_url(self.host, random.choice(self.help_pages))
        self.client.get(route, auth=self._auth)


class SearchUser(HttpUser):
    """ Locust user who does only search requests at a faster rate than both of the previous two.
        Searches are picked randomly from a sample of searches on production.
    """
    host = HOST
    weight = 1  # adjust as needed
    wait_time = between(1, 2)
    _auth = HTTPBasicAuth(*LocustAuthHandler().get_username_and_password())
    searches = json.load(open('./deploy_tests/fourfront/searches.json', 'r'))['searches']

    @task(1)
    def search(self):
        """ Does a random search """
        route = build_url(self.host, random.choice(self.searches))
        self.client.get(route, auth=self._auth)
