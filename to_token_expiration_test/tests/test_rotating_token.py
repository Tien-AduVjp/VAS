from datetime import datetime
from unittest.mock import patch

from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError
from odoo import fields


@tagged('post_install', '-at_install')
class TestTokenExpiration(TransactionCase):

    def setUp(self):
        super(TestTokenExpiration, self).setUp()
        self.token_mixin = self.env['rotating.token.mixin.example.test'].create({
            'company_id': self.env.company.id
        })
        self.token_mixin.company_id.rotating_token_life = 1.0
        self.rotating_token = self.token_mixin.rotating_token_id

    def test_write(self):
        """
        Make sure modifying either Model Name or Record ID is not allowed.
        """
        with self.assertRaises(UserError):
            self.rotating_token.model = 'model.test123'
        with self.assertRaises(UserError):
            self.rotating_token.res_id = -1

        self.rotating_token.with_context(allow_update_model_and_res_id=True).model = 'model.test123'
        self.rotating_token.with_context(allow_update_model_and_res_id=True).res_id = -1

    def test_copy(self):
        with self.assertRaises(UserError):
            self.rotating_token.copy()

    def test_is_expired(self):
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 1, 1, 8, 0, 0)):
            self.rotating_token.expiration = '2021-01-01 07:50:00'
            self.assertTrue(self.rotating_token.is_expired())

            self.rotating_token.expiration = '2021-01-01 09:00:00'
            self.assertFalse(self.rotating_token.is_expired())

    def test_cron_rotate_tokens(self):
        self.token_mixin.unlink()
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 1, 1, 8, 0, 0)):
            self.rotating_token.expiration = '2021-01-02 00:00:00'
            self.assertTrue(self.rotating_token.is_expired())

        self.env['rotating.token'].cron_rotate_tokens()

        # test cron remove tokens linked to records not exist
        self.assertFalse(self.rotating_token.exists())
