from odoo import api, SUPERUSER_ID


def _update_project_on_ticket_from_task(env):
    tickets = env['helpdesk.ticket'].search([('task_id', '!=', False), ('task_id.project_id', '!=', False)])
    for ticket in tickets:
        ticket.write({'project_id': ticket.task_id.project_id.id})


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_project_on_ticket_from_task(env)
