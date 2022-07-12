from odoo import fields, models, api

class AccountTax(models.Model):
    _inherit = 'account.tax'

    import_tax_cost_product_id = fields.Many2one('product.product', string='Import Tax Cost Product',
                                                 compute='_compute_import_tax_cost_product_id',
                                                 help="This product will be used to calculate import landed cost.")

    @api.depends('type_tax_use')
    def _compute_import_tax_cost_product_id(self):
        for r in self:
            if r.type_tax_use in ['purchase', 'none']:
                r.import_tax_cost_product_id = self.env.ref('viin_foreign_trade.to_product_product_import_tax_cost')
            else:
                r.import_tax_cost_product_id = False
