from odoo import api, SUPERUSER_ID
from . import models


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    vietnam_coa_templates = env['account.chart.template']._get_installed_vietnam_coa_templates()
    companies = env['res.company'].with_context(active_test=False).search([
        ('chart_template_id', 'in', vietnam_coa_templates.ids)
        ])
    if companies:
        companies._generate_vietnam_employee_advance_account()
        companies._l10n_vn_update_departments_expense_account()
        companies._update_vietnam_employee_payable_account()
