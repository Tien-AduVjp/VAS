# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _disable_anglo_saxon(env):
    vn_template = env.ref('l10n_vn.vn_template')
    companies_to_fix = env['res.company'].search([
        ('chart_template_id', '=', vn_template.id),
        ('anglo_saxon_accounting', '=', True)
        ])
    if companies_to_fix:
        companies_to_fix.sudo().write({'anglo_saxon_accounting': False})


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _disable_anglo_saxon(env)

