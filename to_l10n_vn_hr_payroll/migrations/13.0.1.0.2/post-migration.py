# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    vietnam = env.ref('base.vn')
    flat_rate_tax_rules = env['personal.tax.rule'].search([
        ('country_id', '=', vietnam.id),
        ('personal_tax_policy', '=', 'flat_rate'),
        ('apply_tax_base_deduction', '=', True)
        ])
    if flat_rate_tax_rules:
        flat_rate_tax_rules.write({
            'apply_tax_base_deduction': False
            })

