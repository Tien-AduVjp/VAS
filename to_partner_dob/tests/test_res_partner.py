from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestResPartner(TransactionCase):

    def setUp(self):
        super(TestResPartner, self).setUp()

    # TC01
    def test_compute_dob(self):
        test_birthday = fields.Date.from_string('1990-02-01')
        test_partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'dob': test_birthday
        })

        result = {
            'birthday': test_partner.dob,
            'dyob': test_partner.dyob,
            'mob': test_partner.mob,
            'yob': test_partner.yob,
        }

        check_vals = {
            'birthday': test_birthday,
            'dyob': test_birthday.day,
            'mob': test_birthday.month,
            'yob': test_birthday.year
        }

        self.assertEqual(check_vals, result, 'Test case TC01')

    # TC02
    def test_empty_dob(self):
        test_partner = self.env['res.partner'].create({
            'name': 'Test Partner'
        })

        result = {
            'birthday': test_partner.dob,
            'dyob': test_partner.dyob,
            'mob': test_partner.mob,
            'yob': test_partner.yob,
        }

        check_vals = {
            'birthday': False,
            'dyob': 0,
            'mob': 0,
            'yob': 0
        }

        self.assertEqual(check_vals, result, 'Test case TC02')
