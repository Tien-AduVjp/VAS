from odoo import api, SUPERUSER_ID


def _update_user_on_ticket_from_team(env):
    tickets = env['helpdesk.ticket'].search([('user_id', '=', False)])
    for ticket in tickets:
        ticket.write({'user_id': ticket.team_id.team_leader_id.id})


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_user_on_ticket_from_team(env)

