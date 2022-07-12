from odoo import fields, models


class ReportHelpdeskTicket(models.Model):
    _inherit = 'report.helpdesk.ticket'

    lead_id = fields.Many2one('crm.lead', string='Lead/Opportunity', readonly=True)

    def _select(self):
        res = super(ReportHelpdeskTicket, self)._select()
        res += ",t.lead_id"
        return res

    def _from(self):
        sql = super(ReportHelpdeskTicket, self)._from()
        sql += """
            LEFT JOIN crm_lead AS lead ON lead.id = t.lead_id
        """
        return sql

    def _group_by(self):
        res = super(ReportHelpdeskTicket, self)._group_by()
        res += ",t.lead_id"
        return res
