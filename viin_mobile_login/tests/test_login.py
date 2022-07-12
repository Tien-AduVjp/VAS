import requests
import json
from odoo.tests.common import TransactionCase, get_db_name
from odoo.tests import tagged


@tagged('post_install', '-at_install', 'external')
class TestLogin(TransactionCase):

    def setUp(self):
        super(TestLogin, self).setUp()

        self.url = self.env['res.users'].search([], limit=1).get_base_url() + '/mobile/login'
        self.db_name = get_db_name()
        self.headers = {'Content-Type': 'application/json'}

        self.data_correct = {"jsonrpc": "2.0",
                             "params": {
                                 "login": 'demo',
                                 "password": 'demo',
                                 "db": self.db_name,
                             }}
        self.data_incorrect = {"jsonrpc": "2.0",
                               "params": {
                                   "login": 'demo',
                                   "password": '88888',
                                   "db": self.db_name,
                               }}

    def test_login_success(self):
        # Test login success, if user info is correct, service will return database's name
        response = requests.request("POST", self.url, headers=self.headers, data=json.dumps(self.data_correct))
        self.assertEqual(response.status_code, 200, "viin_mobile_login: can't connect service")
        result = response.json()['result']
        self.assertEqual(result[0], self.db_name, "viin_mobile_login: with correct account, user can't login")

    def test_login_fail(self):
        # Test login fail, if user info is incorrect, service will return 'null'
        response = requests.request("POST", self.url, headers=self.headers, data=json.dumps(self.data_incorrect))
        self.assertEqual(response.status_code, 200, "viin_mobile_login: can't connect service")
        result = response.json()['result']
        self.assertEqual(result, 'null', "viin_mobile_login: with incorrect account, user can login")
