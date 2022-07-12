from odoo import models, fields


class SalePosReport(models.Model):
    _inherit = "report.pos.order"

    function_id = fields.Many2one('product.function', string='Product Function')

    def _select(self):
        sql = super(SalePosReport, self)._select()
        sql += """,
            f.id AS function_id
        """
        return sql

    def _from(self):
        sql = super(SalePosReport, self)._from()
        sql += """
            LEFT JOIN product_function AS f ON (f.id=pt.function_id)
        """
        return sql

    def _group_by(self):
        sql = super(SalePosReport, self)._group_by()
        sql += """,
            f.id
        """
        return sql

