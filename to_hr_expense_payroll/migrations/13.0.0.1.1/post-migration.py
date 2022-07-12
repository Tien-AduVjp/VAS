from odoo import fields, api, SUPERUSER_ID, _


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([])
    companies._add_hr_expense_to_net_rule()
