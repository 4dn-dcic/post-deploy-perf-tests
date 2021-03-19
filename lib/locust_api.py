import os
import json


# XXX: Passing this header makes the application significantly slower - WHY? -Will 03/19/2021
HEADERS = {
    'Accept': 'application/json'
}


def pdpt_get(*, client, url, auth):
    """ Wrapper function for all gets done by the locust API that will pass application/json """
    return client.get(url, auth=auth)


class LocustAPIException(Exception):
    pass


class LocustAuthHandler:
    """ Contains functions needed to interact with the Locust API in an easy way
        for testing.
    """
    LOCUST_USER_FF = 'LOCUST_USER'
    LOCUST_PASS_FF = 'LOCUST_PASS'
    LOCUST_USER_CGAP = 'LOCUST_USER_CGAP'
    LOCUST_PASS_CGAP = 'LOCUST_PASS_CGAP'

    def __init__(self, auth=None, use_env=True, is_ff=True):
        """ Creates a LocustAPI object

        :param auth (str path):
        :param use_env: whether or not to pull LOCUST_USER/LOCUST_PASS from env or config file
        :param is_ff: whether or not we building a connection to FF or CGAP (access keys differ)
        """
        self.username, self.password = self._load_access_keys(auth=auth, use_env=use_env, is_ff=is_ff)

    @staticmethod
    def _get_creds_from_env(user_key, password_key):
        """ Helper method for below functions"""
        if user_key not in os.environ or password_key not in os.environ:
            raise LocustAPIException('Tried to load Locust auth from environment but'
                                     ' environment variables were not specified (%s)!' % user_key)
        else:
            return os.environ[user_key], os.environ[password_key]

    def _verify_ff_creds_in_env(self):
        """ Verifies that the environment variables we expect for FF are in the environment.

        :return: user, pass if they exist, raise exception otherwise
        """
        return self._get_creds_from_env(self.LOCUST_USER_FF, self.LOCUST_PASS_FF)

    def _verify_cgap_creds_in_env(self):
        """ Verifies that the environment variables we expect for CGAP are in the environment.

        :return: user, pass if they exist, raise exception otherwise
        """
        return self._get_creds_from_env(self.LOCUST_USER_CGAP, self.LOCUST_PASS_CGAP)

    def _load_access_keys(self, auth=None, use_env=True, is_ff=True):
        """ Loads access keys either from the file specified by auth or from environment variables.

        :param auth (str path): file location to use
        :param use_env (bool): whether or not to pull LOCUST_USER/LOCUST_PASS from env or config file
        :param is_ff: whether or not we building a connection to FF or CGAP (access keys differ)
        :return: 2-tuple username, password from config
        """
        if auth is not None and not use_env:  # if passed directly we trust its correct
            with open(auth, 'r') as f:
                raw = json.load(f)
                return raw['username'], raw['password']
        elif use_env:
            if is_ff:
                return self._verify_ff_creds_in_env()
            else:
                return self._verify_cgap_creds_in_env()
        else:
            raise LocustAPIException('No authentication credentials found via file or environment!')

    def get_username_and_password(self):
        return self.username, self.password
