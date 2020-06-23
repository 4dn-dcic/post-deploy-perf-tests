import random
import requests
from requests.auth import HTTPBasicAuth
from locust import HttpUser, TaskSet, task, between
from ..lib.locust_api import LocustAuthHandler


class BasicUser(HttpUser):
    """ Locust user who does basic things on the site at regular intervals. This involves a combination of generic page
        requests and search requests split 75-25. """
    wait_time = between(3, 5)
    _auth = HTTPBasicAuth(*LocustAuthHandler().get_username_and_password())
    item_types = requests.get("/counts?format=json").json['db_es_compare'].keys()

    @task(1)
    def index(self):
        """ Gets the main page - normal request + search AJAX requests """
        self.client.get('/', auth=self._auth)

    @task(3)
    def search(self):
        """ Selects an item type on this portal at random and navigates to its browse page, which
            redirects to search. More lightweight than the index page WRT our application but could
            stress back-end resources.
        """
        t = random.choice(self.item_types)
        self.client.get('/%s' % t, auth=self._auth)


class NavigationUser(HttpUser):
    """ Locust user who "clicks" through all navigation bar links at a faster rate than the
        BasicUser. """
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

    @task(1)
    def data_page(self):
        route = random.choice(self.data_pages)
        self.client.get(route, auth=self._auth)

    def tools_page(self):
        route = random.choice(self.tools_pages)
        self.client.get(route, auth=self._auth)


class SearchUser(HttpUser):
    """ Locust user who does only search requests """
    pass
