from datetime import date

from odoo.addons.to_loan_management.tests.common import TestLoanCommon
from odoo.exceptions import ValidationError
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestLoanCommon(TestLoanCommon):

    @classmethod
    def setUpClass(cls, company=None):
        super().setUpClass(company=company)

    def test_check_interest_float_rate(self):
        self.assertRecordValues(self.interest_float_rate_type_year.floating_rate_ids.sorted(), [
            {'date_to': False},
            {'date_to': date(2022, 10, 14)},
            {'date_to': date(2022, 4, 14)},
        ])

    def test_interest_float_rate_product(self):
        type = self.env['loan.interest.rate.type'].create({
            'type': 'fixed',
            'fixed_rate': 10,
            'interest_rate_period': 'year',
            'product_id': self.env.ref('to_loan_management.service_loan').id,
        })
        with self.assertRaises(ValidationError):
            type.write({'product_id': self.product_consu.id})
