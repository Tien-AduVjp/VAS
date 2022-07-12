from odoo import api, SUPERUSER_ID


def _add_missing_team(env):
    tickets_without_team = env['helpdesk.ticket'].search([('team_id', '=', False)])
    for company in env['res.company'].search([]):
        default_team = company.default_helpdesk_team_id
        tickets = tickets_without_team.filtered(lambda t: t.company_id == company)
        if tickets:
            tickets.write({
                'team_id': default_team.id,
            })


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _add_missing_team(env)
