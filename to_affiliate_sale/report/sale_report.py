from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'
    
    affcode_id = fields.Many2one('affiliate.code', string='Aff. Code', readonly=True)
    affiliate_id = fields.Many2one('res.partner', string="Affiliate", readonly=True)
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['affcode_id'] = ", ac.id AS affcode_id"
        fields['affiliate_id'] = ", ac.partner_id AS affiliate_id"
        from_clause += ' left join affiliate_code AS ac on s.affcode_id = ac.id '
        groupby += ', ac.id, ac.partner_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
    
