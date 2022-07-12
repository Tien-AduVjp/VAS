from odoo import models, api, _
from odoo.exceptions import ValidationError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('is_loan')
    def _onchange_is_loan(self):
        if self.is_loan:
            self.type = 'service'
            self.categ_id = self.env.ref('to_loan_management.product_category_loan_interest')

    @api.constrains('is_loan')
    def _check_product_can_loan(self):
        products = self.filtered(lambda r: not r.is_loan)
        interest_rate_types = self.env['loan.interest.rate.type'].search([('product_id', 'in', products.ids)])
        for type in interest_rate_types:
            raise ValidationError(_("Product '%s' is referenced to Interest Rate Type '%s', you can't edit it.\n"
                              "If you still want to edit, you need to remove it from Interest Type first.")
                              % (type.product_id.display_name, type.display_name))
