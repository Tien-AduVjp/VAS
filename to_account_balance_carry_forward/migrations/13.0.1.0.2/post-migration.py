# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _fix_move_lines(env):
    lines_to_fix = env['account.move.line']
    
    for line in env['account.move.line'].search([('forward_aml_id', '!=', False)]):
        if line.date > line.forward_aml_id.date:
            lines_to_fix |= line
    if lines_to_fix:
        lines_to_fix.write({
            'forward_aml_id': False
            })


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_move_lines(env)

