from odoo import models, fields

class LoyaltyPointsReport(models.Model):
    _inherit = 'loyalty.points.report'

    pos_order_line_id = fields.Many2one('pos.order.line', string='POS Order Line', readonly=True)
    pos_order_id = fields.Many2one('pos.order', string='POS Order', readonly=True)
    session_id = fields.Many2one('pos.session', string='Session', readonly=True)

    def _select(self):
        sql = super(LoyaltyPointsReport, self)._select() + ','
        sql += """
            posl.id AS pos_order_line_id,
            pos.id AS pos_order_id,
            pos.session_id
        """
        return sql


    def _join(self):
        sql = super(LoyaltyPointsReport, self)._join()
        sql += """
            LEFT JOIN pos_order_line AS posl ON posl.id = p.pos_order_line_id
            LEFT JOIN pos_order AS pos ON pos.id = p.pos_order_id
        """
        return sql
