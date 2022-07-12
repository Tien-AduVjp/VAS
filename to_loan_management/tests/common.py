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

        Journal = cls.env['account.journal']
        Account = cls.env['account.account']
        cls.journal_loan_borrow = Journal.search([
            ('company_id', '=', cls.company.id),
            ('type', '=', 'purchase'),
            '|', ('code', '=', 'BLJ'), ('name', 'ilike', 'Borrowing Loans Journal')], limit=1)
        cls.journal_loan_lend = Journal.search([
            ('company_id', '=', cls.company.id),
            ('type', '=', 'sale'),
            '|', ('code', '=', 'LLJ'), ('name', 'ilike', 'Lending Loans Journal')], limit=1)
        cls.account_loan_borrow = Account.search([
            ('company_id', '=', cls.company.id),
            ('user_type_id', '=', cls.env.ref('account.data_account_type_current_liabilities').id)
        ], limit=1)
        cls.account_loan_lend = Account.search([
            ('company_id', '=', cls.company.id),
            ('user_type_id', '=', cls.env.ref('account.data_account_type_current_assets').id)
        ], limit=1)
        cls.journal_bank = Journal.search([
            ('company_id', '=', cls.company.id),
            ('type', '=', 'bank')
        ], limit=1)

        InterestRateType = cls.env['loan.interest.rate.type'].with_context(tracking_disable=True)
        cls.interest_fixed_rate_type_week = InterestRateType.create({
            'name': 'interest_fixed_rate_type_week',
            'type': 'fixed',
            'fixed_rate': 0.7,
            'interest_rate_period': 'week',
        })
        cls.interest_fixed_rate_type_month = InterestRateType.create({
            'name': 'interest_fixed_rate_type_month',
            'type': 'fixed',
            'fixed_rate': 10,
            'interest_rate_period': 'month',
        })
        cls.interest_fixed_rate_type_year = InterestRateType.create({
            'name': 'interest_fixed_rate_type_year',
            'type': 'fixed',
            'fixed_rate': 12,
            'interest_rate_period': 'year',
        })
        cls.interest_float_rate_type_week = InterestRateType.create({
            'name': 'interest_float_rate_type_week',
            'type': 'floating',
            'interest_rate_period': 'week',
            'floating_rate_ids': [
                (0, 0, {'rate': 0.7, 'date_from': date(2022, 10, 3), }),
                (0, 0, {'rate': 1.4, 'date_from': date(2022, 11, 30), }),
            ]
        })
        cls.interest_float_rate_type_month = InterestRateType.create({
            'name': 'interest_float_rate_type_month',
            'type': 'floating',
            'interest_rate_period': 'month',
            'floating_rate_ids': [
                (0, 0, {'rate': 5, 'date_from': date(2021, 10, 15), }),
                (0, 0, {'rate': 10, 'date_from': date(2022, 4, 15), }),
                (0, 0, {'rate': 20, 'date_from': date(2022, 10, 15), })
            ]
        })
        cls.interest_float_rate_type_year = InterestRateType.create({
            'name': 'interest_float_rate_type_year',
            'type': 'floating',
            'interest_rate_period': 'year',
            'floating_rate_ids': [
                (0, 0, {'rate': 20, 'date_from': date(2021, 10, 15), }),
                (0, 0, {'rate': 40, 'date_from': date(2022, 4, 15), }),
                (0, 0, {'rate': 60, 'date_from': date(2022, 10, 15), })
            ]
        })

        cls.setup_accounts()

    @classmethod
    def setup_accounts(cls):
        AccountAccount = cls.env['account.account'].with_context(tracking_disable=True)
        acc_3411 = AccountAccount.create({
            'name': 'Borrowing loans',
            'code': '000_3411',
            'reconcile': True,
            'user_type_id': cls.env.ref('account.data_account_type_current_liabilities').id,
            'company_id': cls.env.company.id,
        })
        acc_1283 = AccountAccount.create({
            'name': 'Lending loans',
            'code': '000_1283',
            'reconcile': True,
            'user_type_id': cls.env.ref('account.data_account_type_current_assets').id,
            'company_id': cls.env.company.id,
        })
        acc_635 = AccountAccount.create({
            'name': 'Financial expenses',
            'code': '000_635',
            'reconcile': False,
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id,
            'company_id': cls.env.company.id,
        })
        acc_515 = AccountAccount.create({
            'name': 'Financial Income',
            'code': '000_515',
            'reconcile': False,
            'user_type_id': cls.env.ref('account.data_account_type_revenue').id,
            'company_id': cls.env.company.id,
        })
        acc_131 = AccountAccount.create({
            'name': 'Trade receivables',
            'code': '000_131',
            'reconcile': True,
            'user_type_id': cls.env.ref('account.data_account_type_receivable').id,
            'company_id': cls.env.company.id,
        })
        acc_331 = AccountAccount.create({
            'name': 'Trade payables',
            'code': '000_331',
            'reconcile': True,
            'user_type_id': cls.env.ref('account.data_account_type_payable').id,
            'company_id': cls.env.company.id,
        })

        cls.company.write({
            'loan_borrowing_journal_id': cls.journal_loan_borrow.id,
            'loan_borrowing_account_id': acc_3411.id,
            'loan_lending_journal_id': cls.journal_loan_lend.id,
            'loan_lending_account_id': acc_1283.id,
        })

        cls.partner.write({
            'property_account_receivable_id': acc_131.id,
            'property_account_payable_id': acc_331.id
        })

        cls.journal_loan_borrow.write({
            'default_account_id': acc_3411.id,
            'account_control_ids': [(6, 0, (acc_3411 | acc_331 | acc_635).ids)],
        })
        cls.journal_loan_lend.write({
            'default_account_id': acc_1283.id,
            'account_control_ids': [(6, 0, (acc_1283 | acc_131 | acc_515).ids)],
        })

        cls.product_category_loan_interest.write({
           'property_account_income_categ_id': acc_515.id,
           'property_account_expense_categ_id': acc_635.id
        })
