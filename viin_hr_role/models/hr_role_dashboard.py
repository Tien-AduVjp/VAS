import json

from odoo import models, fields


class HrRoleDashboard(models.Model):
    _inherit = 'hr.role'

    kanban_dashboard = fields.Text(compute='_kanban_dashboard')
    color = fields.Integer(string='Color Index', default=0)

    def _kanban_dashboard(self):
        for r in self:
            r.kanban_dashboard = json.dumps(r.get_dashboard_datas())

    def get_dashboard_datas(self):
        return {}
