from odoo import fields, models


class ReportHelpdeskTicket(models.Model):
    _inherit = 'report.helpdesk.ticket'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)

    def _select(self):
        res = super(ReportHelpdeskTicket, self)._select()
        res += ",t.sale_order_id"
        return res

    def _from(self):
        sql = super(ReportHelpdeskTicket, self)._from()
        sql += """
            LEFT JOIN sale_order AS sale_order ON sale_order.id = t.sale_order_id
        """
        return sql

    def _group_by(self):
        res = super(ReportHelpdeskTicket, self)._group_by()
        res += ",t.sale_order_id"
        return res
