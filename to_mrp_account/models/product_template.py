from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_cost_structure(self):
        return self.env.ref('to_mrp_account.cost_struct_product_template_action_report').report_action(self.product_variant_id, config=False)
