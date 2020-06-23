import unittest
from unittest import mock
from unittest.mock import MagicMock
from ..locust_api import LocustAPI


class TestLocustAPI(unittest.TestCase):
    def test_load_auth_from_config(self):
        with mock.patch('json.load', return_value={
            'username': 'blah',
            'password': 'halb'
        }):
            api = LocustAPI(auth=__file__, use_env=False)  # this is ok since we patched json.load
            self.assertEqual(api.username, 'blah')
            self.assertEqual(api.password, 'halb')

    @mock.patch.dict('os.environ', {
            LocustAPI.LOCUST_USER: 'blah',
            LocustAPI.LOCUST_PASS: 'halb'
    })
    def test_load_auth_from_env(self):
        LocustAPI._verify_creds_in_env = MagicMock(return_value=True)
        api = LocustAPI(use_env=True)
        self.assertEqual(api.username, 'blah')
        self.assertEqual(api.password, 'halb')


if __name__ == '__main__':
    unittest.main()
