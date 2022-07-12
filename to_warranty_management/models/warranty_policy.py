from odoo import models, fields


class WarrantyPolicy(models.Model):
    _name = 'warranty.policy'
    _description = "Warranty Policy"

    name = fields.Char(string="Name", translate=True)
    product_milestone_id = fields.Many2one('product.milestone', string="Product Milestone", required=True)
    apply_to = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase')], string="Apply to", required=True)
    product_tmpl_id = fields.Many2one('product.template', required=True, ondelete='cascade')

    _sql_constraints = [
        ('warranty_policy_unique',
         'unique(product_milestone_id,apply_to,product_tmpl_id)',
         "Warranty Policy must be unique!"),
    ]

    def _prepare_warranty_claim_policy_data(self):
        return {
            'product_milestone_id': self.product_milestone_id.id,
            'apply_to': self.apply_to,
            }
