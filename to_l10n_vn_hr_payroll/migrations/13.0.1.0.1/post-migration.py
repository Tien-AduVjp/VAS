# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    vietnam = env.ref('base.vn')
    companies = env['res.company'].search([('partner_id.country_id', '=', vietnam.id)])
    companies._add_phone_allowance_to_tax_base_deduction_vietnam()

