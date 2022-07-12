from odoo import models, fields


class SalePosReport(models.Model):
    _inherit = 'report.pos.order'

    collection_id = fields.Many2one('product.collection', string='Product Collection')

    def _select(self):
        sql = super(SalePosReport, self)._select()
        sql += """,
            col.id AS collection_id
        """
        return sql

    def _from(self):
        sql = super(SalePosReport, self)._from()
        sql += """
            LEFT JOIN product_collection AS col ON (col.id=pt.collection_id)
        """
        return sql

    def _group_by(self):
        sql = super(SalePosReport, self)._group_by()
        sql += """,
            col.id
        """
        return sql

