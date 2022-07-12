# -*- coding: utf-8 -*-

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_cost_structure(self):
        return self.env.ref('to_mrp_account.cost_struct_product_template_action_report').report_action(self, config=False)
