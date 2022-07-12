from . import models
from odoo import api, SUPERUSER_ID


def _generate_currency_conversion_difference_journal_if_not_exists(env):
    Journal = env['account.journal']
    for company in env['res.company'].search([('chart_template_id', '!=', False)]):
        journal = Journal.search([('code', '=', 'CCDJ'), ('company_id', '=', company.id)], limit=1)
        if not journal:
            journal = Journal.create(company._prepare_currency_conversion_journal_data())
        company.write({'currency_conversion_diff_journal_id': journal.id})


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_currency_conversion_difference_journal_if_not_exists(env)
