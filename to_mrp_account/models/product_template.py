# -*- coding: utf-8 -*-

from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_cost_structure(self):
        products = self.mapped('product_variant_id')
        return self.env.ref('to_mrp_account.cost_struct_product_template_action_report').report_action(products, config=False)
