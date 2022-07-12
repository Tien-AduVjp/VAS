from odoo import fields, models

class ReportHelpdeskTicket(models.Model):
    _inherit = 'report.helpdesk.ticket'

    severity_level = fields.Selection([
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor/Medium'),
        ('low', 'Low')
        ], string='Severity', readonly=True)

    def _select(self):
        res = super(ReportHelpdeskTicket, self)._select()
        res += ",t.severity_level"
        return res

    def _group_by(self):
        res = super(ReportHelpdeskTicket, self)._group_by()
        res += ",t.severity_level"
        return res

