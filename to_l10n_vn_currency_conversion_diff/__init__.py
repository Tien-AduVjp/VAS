from odoo import api, SUPERUSER_ID

from . import models


def _update_currency_conversion_difference_accounts(env):
    vietnam_coa = env['account.chart.template']._get_installed_vietnam_coa_templates()
    companies = env['res.company'].search([('chart_template_id', 'in', vietnam_coa.ids)])
    for company in companies:
        ccd_income_account, ccd_expense_account = company._get_currency_conversion_diff_accounts()
        company.write({
            'income_currency_conversion_diff_account_id': ccd_income_account.id,
            'expense_currency_conversion_diff_account_id': ccd_expense_account.id,
            })


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_currency_conversion_difference_accounts(env)
