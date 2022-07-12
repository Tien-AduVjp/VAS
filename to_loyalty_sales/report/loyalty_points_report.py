from odoo import models, fields

class LoyaltyPointsReport(models.Model):
    _inherit = 'loyalty.points.report'

    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Line', readonly=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)


    def _select(self):
        sql = super(LoyaltyPointsReport, self)._select() + ','
        sql += """
            sol.id AS sale_order_line_id,
            so.id AS sale_order_id
        """
        return sql

    def _join(self):
        sql = super(LoyaltyPointsReport, self)._join()
        sql += """
            LEFT JOIN sale_order_line AS sol ON sol.id = p.sale_order_line_id
            LEFT JOIN sale_order AS so ON so.id = p.sale_order_id
        """
        return sql
