from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'


    def _get_deferral_analytic_tags(self, deferral_type):
        self.ensure_one()
        if deferral_type == 'cost':
            return self.cost_deferral_category_id.sudo().analytic_tag_ids
        elif deferral_type == 'revenue':
            return self.revenue_deferral_category_id.sudo().analytic_tag_ids
        else:
            return False

    def _get_deferral_analytic_account(self, deferral_type):
        self.ensure_one()
        if deferral_type == 'cost':
            return self.cost_deferral_category_id.account_analytic_id
        elif deferral_type == 'revenue':
            return self.revenue_deferral_category_id.account_analytic_id
        else:
            return False
