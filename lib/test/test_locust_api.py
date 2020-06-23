import unittest
from unittest import mock
from unittest.mock import MagicMock
from ..locust_api import LocustAuthHandler


class TestLocustAPI(unittest.TestCase):
    def test_load_auth_from_config(self):
        with mock.patch('json.load', return_value={
            'username': 'blah',
            'password': 'halb'
        }):
            api = LocustAuthHandler(auth=__file__, use_env=False)  # this is ok since we patched json.load
            self.assertEqual(api.username, 'blah')
            self.assertEqual(api.password, 'halb')

    @mock.patch.dict('os.environ', {
            LocustAuthHandler.LOCUST_USER: 'blah',
            LocustAuthHandler.LOCUST_PASS: 'halb'
    })
    def test_load_auth_from_env(self):
        LocustAuthHandler._verify_creds_in_env = MagicMock(return_value=True)
        api = LocustAuthHandler(use_env=True)
        self.assertEqual(api.username, 'blah')
        self.assertEqual(api.password, 'halb')


if __name__ == '__main__':
    unittest.main()
