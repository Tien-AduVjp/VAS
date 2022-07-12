from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    function_id = fields.Many2one('product.function', string='Product Function')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['function_id'] = ', f.id AS function_id'
        from_clause += ' LEFT JOIN product_function AS f ON f.id = t.function_id '
        groupby += ', f.id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
