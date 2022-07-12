from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.product'

    def _get_direct_fee_definitions(self):
        return self.mapped('product_tmpl_id').mapped('fee_definition_ids')

    def _get_nested_fee_definitions(self, visited_fees=None):
        """
        get nested fee definitions of self
        """
        if visited_fees is None:
            visited_fees = []
        fee_definition_ids = self.mapped('product_tmpl_id.fee_definition_ids')
        for fee_definition_id in fee_definition_ids:
            if fee_definition_id in visited_fees:
                break
            visited_fees.append(fee_definition_id)
            fee_definition_ids += fee_definition_id.product_id._get_nested_fee_definitions(visited_fees=visited_fees)
        return fee_definition_ids
