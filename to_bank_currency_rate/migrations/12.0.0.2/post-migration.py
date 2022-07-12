# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    recompute_needed_invoices = env['account.invoice'].search([('amount_untaxed', '=', 0.0)])
    for invoice in recompute_needed_invoices:
        invoice._compute_amount()

