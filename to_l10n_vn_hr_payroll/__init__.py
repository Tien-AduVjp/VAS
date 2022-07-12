from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    vietnam = env.ref('base.vn')
    companies = env['res.company'].search([('partner_id.country_id', '=', vietnam.id)])
    companies._set_payroll_contrib_data()
    companies._generate_personal_tax_rules()
    companies._add_phone_allowance_to_tax_base_deduction_vietnam()
