from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_product_tmp_allow_generate_code(self):
        product_valid = self.filtered(lambda r: r.company_id.auto_product_default_code_generation)
        if self.env.company.auto_product_default_code_generation:
            product_valid |= (self - product_valid).filtered(lambda r: not r.company_id)
        return product_valid

    @api.onchange('name', 'categ_id')
    def onchange_name_categ_id(self):
        if self._get_product_tmp_allow_generate_code() and (not self.default_code or not self._origin):
            self.default_code = self._generate_prod_code()

    def _generate_prod_code(self):
        self.ensure_one()
        default_code_prefix = self.categ_id and self.categ_id.get_product_code_prefix() or self._get_code_from_name()
        product_default_code_sequence = self.categ_id and self.categ_id.get_ir_sequence_id() or 'product.default_code'
        code = ''
        if default_code_prefix:
            code += default_code_prefix
            code += self.env['ir.sequence'].next_by_code(product_default_code_sequence)
        return code

    def update_default_code(self):
        self._get_product_tmp_allow_generate_code().product_variant_ids.update_default_code()

    def _get_code_from_name(self):
        self.ensure_one()
        default_code_prefix = ''
        if self.name:
            for i in self.name.upper().split():
                default_code_prefix += i[0]
        return default_code_prefix

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if vals.get('attribute_line_ids', False):
            self._get_product_tmp_allow_generate_code().product_variant_ids.filtered(lambda v: not v.default_code).update_default_code()
        return res

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        records = super(ProductTemplate, self).create(vals_list)
        records._get_product_tmp_allow_generate_code().product_variant_ids.filtered(lambda v: not v.default_code).update_default_code()
        return records
