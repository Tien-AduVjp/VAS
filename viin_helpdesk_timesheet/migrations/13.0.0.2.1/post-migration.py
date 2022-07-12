from odoo import api, SUPERUSER_ID


def _fix_ticket_project_task_discrepancy(env):
    tickets = env['helpdesk.ticket'].with_context(active_test=False).search([])
    to_recompute = tickets.filtered(lambda t: t.task_id and t.task_id.project_id != t.project_id)
    to_recompute._compute_project_id()

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_ticket_project_task_discrepancy(env)
