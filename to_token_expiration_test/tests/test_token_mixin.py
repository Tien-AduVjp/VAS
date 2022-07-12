from datetime import datetime
from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged
from odoo import fields


@tagged('post_install', '-at_install')
class TestTokenExpiration(TransactionCase):

    def setUp(self):
        super(TestTokenExpiration, self).setUp()
        self.token_mixin = self.env['rotating.token.mixin.example.test'].create({
            'company_id': self.env.company.id
        })
        self.company = self.env.company
        self.company.rotating_token_life = False

    def test_constrains_rotating_token_life(self):
        """ test rotating_token_life must be greater than or equal to zero """
        with self.assertRaises(ValidationError):
            self.company.rotating_token_life = -1
        with self.assertRaises(ValidationError):
            self.company.rotating_token_life = -2
        with self.assertRaises(ValidationError):
            self.company.rotating_token_life = -11.593

        self.company.rotating_token_life = 0
        self.company.rotating_token_life = 10

    def test_compute_access_token(self):
        self.assertNotEqual(self.token_mixin.access_token, False)
        self.token_mixin.rotating_token_id = None
        self.assertFalse(self.token_mixin.access_token)

    def test_ensure_rotating_token(self):
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 1, 1, 8, 0, 0)):
            self.token_mixin.rotating_token_id.expiration = '2021-01-01 07:00:00'
            self.assertTrue(self.token_mixin.rotating_token_id.is_expired())

        self.token_mixin._ensure_rotating_token()
        self.assertFalse(self.token_mixin.rotating_token_id.is_expired())

    def test_get_token_lifetime(self):
        self.assertFalse(self.token_mixin._get_token_lifetime())
        self.token_mixin.company_id.rotating_token_life = 2.0
        self.assertEqual(self.token_mixin._get_token_lifetime(), 2.0)

    def test_get_expiration_date(self):
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 1, 1, 8, 0, 0)):
             self.token_mixin.company_id.rotating_token_life = 3.0
             actual_expiration_date = self.token_mixin._get_expiration_date().strftime('%Y-%m-%d %H:%M:%S')
             self.assertEqual(actual_expiration_date, '2021-01-04 08:00:00')

        self.token_mixin.company_id.rotating_token_life = 0
        self.assertFalse(self.token_mixin._get_expiration_date())

    def test_generate_token(self):
        # make sure the token is generated and ready to use after creating the record
        record = self.env['rotating.token.mixin.example.test'].create({
            'company_id': self.env.company.id
        })
        self.assertNotEqual(record.rotating_token_id, False)
        self.assertNotEqual(record.access_token, False)

    def test_rotate_token(self):
        """
        Make sure old tokens are deleted and new tokens are created, this new token must not expire
        """
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 1, 1, 8, 0, 0)):
            self.token_mixin.rotating_token_id.expiration = '2021-01-01 06:00:00'
            self.assertTrue(self.token_mixin.rotating_token_id.is_expired())

        old_token_id = self.token_mixin.rotating_token_id.id
        self.token_mixin.rotate_token()
        new_token_id = self.token_mixin.rotating_token_id.id

        self.assertNotEqual(old_token_id, new_token_id)
        self.assertFalse(self.token_mixin.rotating_token_id.is_expired())
