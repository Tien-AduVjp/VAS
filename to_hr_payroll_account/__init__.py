from . import models
from . import wizard

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    company_obj = env['res.company']
    company_obj._generate_salary_account_journals()
    company_obj._fill_journal_to_payslips()
