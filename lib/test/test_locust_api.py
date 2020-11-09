import unittest
from unittest import mock
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
            LocustAuthHandler.LOCUST_USER_FF: 'blah',
            LocustAuthHandler.LOCUST_PASS_FF: 'halb'
    })
    def test_load_auth_from_ff_env(self):
        api = LocustAuthHandler(use_env=True)
        self.assertEqual(api.username, 'blah')
        self.assertEqual(api.password, 'halb')

    @mock.patch.dict('os.environ', {
        LocustAuthHandler.LOCUST_USER_CGAP: 'blah',
        LocustAuthHandler.LOCUST_PASS_CGAP: 'halb'
    })
    def test_load_auth_from_cgap_env(self):
        api = LocustAuthHandler(use_env=True, is_ff=False)  # do CGAP
        self.assertEqual(api.username, 'blah')
        self.assertEqual(api.password, 'halb')


if __name__ == '__main__':
    unittest.main()
