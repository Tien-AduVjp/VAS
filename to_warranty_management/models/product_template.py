from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    warranty_period = fields.Integer(string='Warranty period (months)')
    warranty_policy_ids = fields.One2many('warranty.policy', 'product_tmpl_id', string="Warranty Policy", groups="to_warranty_management.group_warranty_user")

    @api.constrains('warranty_policy_ids')
    def _check_constrains_milestone(self):
        for r in self:
            policy_for_sale_ids = r.mapped('warranty_policy_ids').filtered(lambda p: p.apply_to == 'sale')
            policy_for_purchase_ids = r.warranty_policy_ids - policy_for_sale_ids
            sale_categ_ids = policy_for_sale_ids.mapped('product_milestone_id.uom_id.category_id')
            purchase_categ_ids = policy_for_purchase_ids.mapped('product_milestone_id.uom_id.category_id')

            if len(policy_for_sale_ids) > len(sale_categ_ids) or len(policy_for_purchase_ids) > len(purchase_categ_ids):
                raise ValidationError(_("You can not create more milestone that have the same category with an existing milestone"))
