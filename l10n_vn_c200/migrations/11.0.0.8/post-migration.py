# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    vn_chart_id = env.ref('l10n_vn.vn_template').id
    journals = env['account.journal'].search([
        ('type', 'in', ('sale', 'purchase')),
        ('refund_sequence', '=', False),
        ('company_id.chart_template_id','=',vn_chart_id)])
    if journals:
        journals.write({'refund_sequence': True})

