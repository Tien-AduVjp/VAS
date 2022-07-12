from odoo import api, SUPERUSER_ID


def _update_stage_on_ticket_if_not_exists(env):
    tickets = env['helpdesk.ticket'].search([('stage_id', '=', False)])
    for ticket in tickets:
        ticket.write({'stage_id': ticket.team_id.stage_ids and ticket.team_id.stage_ids[0].id or False})


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_stage_on_ticket_if_not_exists(env)

