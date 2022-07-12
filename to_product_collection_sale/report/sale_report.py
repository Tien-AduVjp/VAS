from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    collection_id = fields.Many2one('product.collection', string='Product Collection')
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['collection_id'] = ", col.id AS collection_id"
        from_clause += ' LEFT JOIN product_collection AS col ON col.id = t.collection_id '
        groupby += ', col.id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)    