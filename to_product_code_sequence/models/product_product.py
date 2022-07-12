from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    @api.onchange('name', 'categ_id')
    def onchange_name_categ_id(self):
        if not self.default_code or not self._origin:
            self.default_code = self._generate_prod_code()

    def update_default_code(self):
        for r in self:
            r.default_code = r._generate_prod_code()

    def _get_code_from_name(self):
        self.ensure_one()
        default_code_prefix = ''
        if self.name:
            for i in self.name.upper().split():
                default_code_prefix += i[0]
        return default_code_prefix

    def _generate_prod_code(self):
        self.ensure_one()
        default_code_prefix = self.categ_id and self.categ_id.get_product_code_prefix() or self._get_code_from_name()
        product_default_code_sequence = self.categ_id and self.categ_id.get_ir_sequence_id() or 'product.default_code'
        code = ''
        if default_code_prefix:
            code += default_code_prefix
            code += self.env['ir.sequence'].next_by_code(product_default_code_sequence)
        return code
