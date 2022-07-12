from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    warranty_period = fields.Integer(string='Warranty period (months)')
    warranty_policy_ids = fields.One2many('warranty.policy', 'product_tmpl_id', string='Warranty Policy', groups='to_warranty_management.group_warranty_user')

    _sql_constraints = [
        (
            'check_warranty_period_not_negative',
            'CHECK(warranty_period >= 0)',
            "The warranty period cannot be a negative number",
        ),
    ]

    @api.constrains('warranty_policy_ids')
    def _check_constrains_milestone(self):
        for r in self:
            policy_for_sales = r.mapped('warranty_policy_ids').filtered(lambda p: p.apply_to == 'sale')
            policy_for_purchases = r.warranty_policy_ids - policy_for_sales
            sale_categorys = policy_for_sales.mapped('product_milestone_id.uom_id.category_id')
            purchase_categorys = policy_for_purchases.mapped('product_milestone_id.uom_id.category_id')

            if len(policy_for_sales) > len(sale_categorys) or len(policy_for_purchases) > len(purchase_categorys):
                raise ValidationError(_("You can not create more milestone that have the same category with an existing milestone"))
