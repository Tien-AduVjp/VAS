from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    same_default_code_product_id = fields.Many2one('product.product', string='Product with same Internal Reference',
                                                   compute='_compute_same_default_code_product_id',
                                                   readonly=False)

    @api.constrains('default_code')
    def constrains_default_code(self):
        self.flush()
        records_to_check = self.filtered(lambda r: r.company_id.check_unique_product_default_code)

        if self.env.company.check_unique_product_default_code:
            records_to_check |= (self - records_to_check).filtered(lambda r: not r.company_id)

        records_to_check._compute_same_default_code_product_id()
        for r in records_to_check:
            if r.same_default_code_product_id:
                raise ValidationError(_("Invalid Code! The code '%s' has been assigned to the product '%s'."
                                        " Please input another code!")
                                        % (r.default_code, r.same_default_code_product_id.display_name))

    @api.depends('default_code')
    def _compute_same_default_code_product_id(self):
        for r in self:
            domain = [('id', '!=', r.id), ('default_code', '=', r.default_code)]

            overlapping_product = self.search(domain, limit=1)
            r.same_default_code_product_id = bool(r.default_code) and overlapping_product or False
