from . import models
from odoo import api, SUPERUSER_ID
from odoo.addons.to_l10n_vn_hr_payroll_account.models.res_company import  SALARY_RULES_ACCOUNTS_MAP

SALARY_RULES_ACCOUNTS_MAP['MODED'] = {'account_debit': '1388', 'account_credit': '334'}

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    env['res.company'].search([]).sudo()._update_vietnam_meal_salary_rule_accounts()
