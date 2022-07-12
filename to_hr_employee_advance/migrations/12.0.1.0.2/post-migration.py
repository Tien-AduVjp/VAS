from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for company_id in env['res.company'].search([('chart_template_id', '!=', False)]):
        company_id.create_employee_advance_journal_if_not_exists()
