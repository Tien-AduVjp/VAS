from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.category'

    product_code_prefix = fields.Char(string='Product Code Prefix',
                                      help="The text string to be used as the prefix of the auto-generated default codes of the"
                                      " category's products.")
    ir_sequence_id = fields.Many2one('ir.sequence', string='Product Sequence')

    def get_product_code_prefix(self):
        return self.product_code_prefix or (self.parent_id and self.parent_id.get_product_code_prefix())

    def get_ir_sequence_id(self):
        return self.ir_sequence_id and self.ir_sequence_id.code or (self.parent_id and self.parent_id.get_ir_sequence_id() or '')
