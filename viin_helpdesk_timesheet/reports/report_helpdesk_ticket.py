from odoo import fields, models


class ReportHelpdeskTicket(models.Model):
    _inherit = 'report.helpdesk.ticket'

    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    task_id = fields.Many2one('project.task', string='Task', readonly=True)

    def _select(self):
        res = super(ReportHelpdeskTicket, self)._select()
        res += ",t.project_id, t.task_id"
        return res

    def _from(self):
        sql = super(ReportHelpdeskTicket, self)._from()
        sql += """
            LEFT JOIN project_project AS proj ON proj.id = t.project_id
            LEFT JOIN project_task AS task ON task.id = t.task_id
        """
        return sql

    def _group_by(self):
        res = super(ReportHelpdeskTicket, self)._group_by()
        res += ",t.project_id, t.task_id"
        return res
