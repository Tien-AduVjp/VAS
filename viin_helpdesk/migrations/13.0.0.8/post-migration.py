from odoo import api, SUPERUSER_ID


def _update_sla_line(env):
    sla_lines = env['helpdesk.sla.line'].search([('reached_datetime', '=', False)])
    sla_lines._compute_reached_datetime()

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_sla_line(env)
