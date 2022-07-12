from odoo import models, _
from odoo.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def unlink(self):
        for r in self:
            if r == self.env.ref('viin_foreign_trade.to_product_product_import_tax_cost'):
                raise UserError(_("You can not delete product `%s`. Because it is used for import landed cost.", r.name))
        return super(ProductProduct, self).unlink()
