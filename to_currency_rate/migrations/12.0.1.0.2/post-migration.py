# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    Rate = env['res.currency.rate']
    rate_ids = Rate.search([])
    if rate_ids:
        rate_ids._compute_inverse_rate()

