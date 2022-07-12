# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['hr.employee'].sudo().search([])._apply_vietnam_empoloyee_payable_account()

