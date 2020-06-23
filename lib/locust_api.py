import os
import json


class LocustAPIException(Exception):
    pass


class LocustAuthHandler:
    """ Contains functions needed to interact with the Locust API in an easy way
        for testing.
    """
    LOCUST_USER = 'LOCUST_USER'
    LOCUST_PASS = 'LOCUST_PASS'

    def __init__(self, auth=None, use_env=True):
        """ Creates a LocustAPI object

        :param auth (str path):
        :param use_env: whether or not to pull LOCUST_USER/LOCUST_PASS from env or config file
        """
        self.username, self.password = self._load_access_keys(auth=auth, use_env=use_env)

    def _verify_creds_in_env(self):
        """ Verifies that the environment variables we expect are in the environment.

        :return: True if the env variables exist, False otherwise
        """
        if self.LOCUST_USER not in os.environ or self.LOCUST_PASS not in os.environ:
            return False
        else:
            return True

    def _load_access_keys(self, auth=None, use_env=True):
        """ Loads access keys either from the file specified by auth or from environment variables.

        :param auth (str path): file location to use
        :param use_env (bool): whether or not to pull LOCUST_USER/LOCUST_PASS from env or config file
        :return: 2-tuple username, password from config
        """
        if auth is not None and not use_env:
            with open(auth, 'r') as f:
                raw = json.load(f)
                return raw['username'], raw['password']
        elif use_env:
            if not self._verify_creds_in_env():
                raise LocustAPIException('Tried to load Locust auth from environment but'
                                         'environment variables were not specified!')
            else:
                return os.environ[self.LOCUST_USER], os.environ[self.LOCUST_PASS]

    def get_username_and_password(self):
        return self.username, self.password
