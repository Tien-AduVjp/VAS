from datetime import date

from odoo.tests.common import SavepointCase


class TestLoanCommon(SavepointCase):

    @classmethod
    def setUpClass(cls, company=None):
        super().setUpClass()
        if company:
            cls.env.company = company
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref('base.res_partner_1')
        cls.currency_vnd = cls.env.ref('base.VND')
        cls.product_category_loan_interest = cls.env.ref('to_loan_management.product_category_loan_interest')
        cls.account_payment_method_manual_in = cls.env.ref('account.account_payment_method_manual_in')
        cls.product_consu = cls.env.ref('product.product_delivery_02')
        cls.product_service = cls.env.ref('product.product_product_1')
        cls.product_loan = cls.env.ref('to_loan_management.service_loan')
        cls.company = cls.env.company
        cls.journal_loan_borrow = cls.env['account.journal'].search([
            ('company_id', '=', cls.company.id),
            ('type', '=', 'purchase'),
            '|', ('code', '=', 'BLJ'), ('name', 'ilike', 'Borrowing Loans Journal')], limit=1)
        cls.journal_loan_lend = cls.env['account.journal'].search([
            ('company_id', '=', cls.company.id),
            ('type', '=', 'sale'),
            '|', ('code', '=', 'LLJ'), ('name', 'ilike', 'Lending Loans Journal')], limit=1)
        cls.account_loan_borrow = cls.env['account.account'].search([
            ('company_id', '=', cls.company.id),
            ('user_type_id', '=', cls.env.ref('account.data_account_type_current_liabilities').id)
        ], limit=1)
        cls.account_loan_lend = cls.env['account.account'].search([
            ('company_id', '=', cls.company.id),
            ('user_type_id', '=', cls.env.ref('account.data_account_type_current_assets').id)
        ], limit=1)
        cls.journal_bank = cls.env['account.journal'].search([
            ('company_id', '=', cls.company.id),
            ('type', '=', 'bank')
        ], limit=1)
        cls.interest_flat_rate_type_week = cls.env['loan.interest.rate.type'].create({
            'name': 'interest_flat_rate_type_week',
            'type': 'flat',
            'flat_rate': 0.7,
            'interest_rate_period': 'week',
        })
        cls.interest_flat_rate_type_month = cls.env['loan.interest.rate.type'].create({
            'name': 'interest_flat_rate_type_month',
            'type': 'flat',
            'flat_rate': 10,
            'interest_rate_period': 'month',
        })
        cls.interest_flat_rate_type_year = cls.env['loan.interest.rate.type'].create({
            'name': 'interest_flat_rate_type_year',
            'type': 'flat',
            'flat_rate': 12,
            'interest_rate_period': 'year',
        })
        cls.interest_float_rate_type_week = cls.env['loan.interest.rate.type'].create({
            'name': 'interest_float_rate_type_week',
            'type': 'floating',
            'interest_rate_period': 'week',
            'floating_rate_ids': [
                (0, 0, {'rate': 0.7, 'date_from': date(2022, 10, 3), }),
                (0, 0, {'rate': 1.4, 'date_from': date(2022, 11, 30), }),
            ]
        })
        cls.interest_float_rate_type_month = cls.env['loan.interest.rate.type'].create({
            'name': 'interest_float_rate_type_month',
            'type': 'floating',
            'interest_rate_period': 'month',
            'floating_rate_ids': [
                (0, 0, {'rate': 5, 'date_from': date(2021, 10, 15), }),
                (0, 0, {'rate': 10, 'date_from': date(2022, 4, 15), }),
                (0, 0, {'rate': 20, 'date_from': date(2022, 10, 15), })
            ]
        })
        cls.interest_float_rate_type_year = cls.env['loan.interest.rate.type'].create({
            'name': 'interest_float_rate_type_year',
            'type': 'floating',
            'interest_rate_period': 'year',
            'floating_rate_ids': [
                (0, 0, {'rate': 20, 'date_from': date(2021, 10, 15), }),
                (0, 0, {'rate': 40, 'date_from': date(2022, 4, 15), }),
                (0, 0, {'rate': 60, 'date_from': date(2022, 10, 15), })
            ]
        })
