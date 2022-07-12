import logging
from odoo import fields
from odoo.tests import Form
from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        
        # Create accounting user.
        account_user = cls.env['res.users'].with_context(no_reset_password=True,tracking_disable=True).create({
            'name': 'Accountant',
            'login': 'accountant@example.com',
            'groups_id': [(6, 0, cls.env.user.groups_id.ids),
                          (4, cls.env.ref('account.group_account_manager').id),
                          (4, cls.env.ref('account.group_account_user').id),
                          (4, cls.env.ref('analytic.group_analytic_accounting').id),
                          (4, cls.env.ref('analytic.group_analytic_tags').id)],
        })
        account_user.partner_id.email = 'accountant@example.com'
        cls.env = cls.env(user=account_user)
        
        chart_template = cls.env.ref('l10n_generic_coa.configurable_chart_template', raise_if_not_found=False)
        if not chart_template:
            _logger.warning("Test skipped because there is no chart of account defined ...")
            cls.skipTest(cls, "No Chart of account found")
        company_id = cls.env.company.id
        # Accounts
        Account = cls.env['account.account']
        cls.account_cash = Account.search([
            ('name', '=', 'Cash'),
            ('user_type_id', '=', cls.env.ref('account.data_account_type_liquidity').id),
            ('reconcile', '=', False),
            ('company_id', '=', company_id)], limit=1)
        cls.account_bank = Account.search([
            ('name', '=', 'Bank'),
            ('user_type_id', '=', cls.env.ref('account.data_account_type_liquidity').id),
            ('reconcile', '=', False),
            ('company_id', '=', company_id)], limit=1)
        cls.account_unrealized_revenue = Account.search([
            ('user_type_id', '=', cls.env.ref('account.data_account_type_current_liabilities').id),
            ('reconcile', '=', False),
            ('company_id', '=', company_id)], limit=1)
        cls.account_long_term_cost = Account.search([
            ('user_type_id', '=', cls.env.ref('account.data_account_type_non_current_assets').id),
            ('reconcile', '=', False),
            ('company_id', '=', company_id)], limit=1)
        cls.account_expense = Account.search([
            ('user_type_id', '=', cls.env.ref('account.data_account_type_current_assets').id),
            ('reconcile', '=', False),
            ('company_id', '=', company_id)], limit=1)
        cls.account_revenue = Account.search([
            ('user_type_id', '=', cls.env.ref('account.data_account_type_revenue').id),
            ('reconcile', '=', False),
            ('company_id', '=', company_id)], limit=1)
        
        # Journals
        Journal = cls.env['account.journal'].with_context(tracking_disable=True)
        cls.journal_revenue_deferral = Journal.create({
            'name': 'Revenue Deferral',
            'type': 'sale',
            'code': 'INVT',
            'default_debit_account_id': cls.account_revenue.id,
            'default_credit_account_id': cls.account_cash.id,
            'company_id': company_id
        })
        cls.journal_cost_deferral = Journal.create({
            'name': 'Cost Deferral',
            'type': 'purchase',
            'code': 'BILLT',
            'default_debit_account_id': cls.account_expense.id,
            'default_credit_account_id': cls.account_expense.id,
            'company_id': company_id
        })
        
        # Default deferral category
        DeferralCategory= cls.env['cost.revenue.deferral.category'].with_context(tracking_disable=True)
        cls.revenue_deferral_category = DeferralCategory.create({
            'name': 'revenue deferral category',
            'journal_id': cls.journal_revenue_deferral.id,
            'deferred_account_id': cls.account_unrealized_revenue.id,
            'recognition_account_id': cls.account_revenue.id,
            'type': 'revenue',
            'method_time': 'number',
            'method_number': 2,
            'method_period': 1,
        })
        cls.revenue_deferral_category_end = DeferralCategory.create({
            'name': 'revenue deferral category 2',
            'journal_id': cls.journal_revenue_deferral.id,
            'deferred_account_id': cls.account_unrealized_revenue.id,
            'recognition_account_id': cls.account_revenue.id,
            'type': 'revenue',
            'method_time': 'end',
            'method_period': 1,
            'method_end': fields.Date.subtract(fields.Date.today(), days=1)
        })
        cls.cost_deferral_category = DeferralCategory.create({
            'name': 'cost deferral category',
            'journal_id': cls.journal_cost_deferral.id,
            'deferred_account_id': cls.account_long_term_cost.id,
            'recognition_account_id': cls.account_expense.id,
            'type': 'cost',
            'method_time': 'number',
            'method_number': 2,
            'method_period': 1,
        })
        
        cls.product_A = cls.env['product.product'].with_context(tracking_disable=True).create({
            'name': 'Product A',
            'cost_deferral_category_id': cls.cost_deferral_category.id,
            'revenue_deferral_category_id': cls.revenue_deferral_category.id,
        })
        
        # Cost/revenue deferral
        cls.revenue_deferral = cls.create_deferral('revenue', cls.revenue_deferral_category, 20000)
        cls.cost_deferral = cls.create_deferral('cost', cls.cost_deferral_category, 20000)
        
    @classmethod
    def create_deferral(cls, type, category, value):
        f = Form(cls.env['cost.revenue.deferral'].with_context(default_type=type), view="to_cost_revenue_deferred.cost_revenue_deferral_form")
        f.name = 'RD' if type == 'revenue' else 'CD'
        f.date = fields.Date.to_date('2022-01-01')
        f.value = value
        f.deferral_category_id = category
        return f.save()
