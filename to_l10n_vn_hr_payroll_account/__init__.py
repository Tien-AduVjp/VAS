from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    vn_coa = env.ref('l10n_vn.vn_template')
    companies = env['res.company'].sudo().search([('chart_template_id', '=', vn_coa.id)])
    companies._update_vietnam_salary_account_journal_default_accounts()
    companies._update_vietnam_salary_rules_accounts()
    companies._update_departments_expense_account()
    env['hr.employee'].sudo().search([])._apply_vietnam_empoloyee_payable_account()
    
