# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _fix_null_location_id_in_repair_line(env):
    # for unknown reason (it could be turn a stored field into non-store field),
    # some repair lines have null in location_id
    # this is to fix such the error
    error_lines = env['repair.line'].sudo().search([('location_id', '=', False)])
    for repair in error_lines.mapped('repair_id'):
        error_lines.filtered(lambda l: l.repair_id == repair).write({
            'location_id': repair.location_id.id
            })


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_null_location_id_in_repair_line(env)

