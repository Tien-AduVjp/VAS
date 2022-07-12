from odoo import fields, models, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    export_tax_ids = fields.Many2many('account.tax', 'product_export_taxes_rel', 'prod_id', 'tax_id',
                                      string="Exporting Taxes",
                                      domain=[('type_tax_use','in',['sale', 'none'])]
                                      )

    import_tax_ids = fields.Many2many('account.tax', 'product_import_taxes_rel', 'prod_id', 'tax_id',
                                      string="Importing Taxes",
                                      domain=[('type_tax_use','in',['purchase', 'none'])]
                                      )

    def unlink(self):
        import_tax_cost_product = self.env.ref('viin_foreign_trade.to_product_product_import_tax_cost')
        for r in self:
            if import_tax_cost_product in r.product_variant_ids:
                raise UserError(_("You can not delete product `%s`. Because it is used for import landed cost.", import_tax_cost_product.name))
        return super(ProductTemplate, self).unlink()
