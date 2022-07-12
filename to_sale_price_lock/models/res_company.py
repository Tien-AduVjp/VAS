from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    def _get_group_sale_price_modifying(self):
        return self.env.ref('sales_team.group_sale_salesman_all_leads')
    
    @api.model
    def _get_group_domain(self):
        return [('category_id.id', '=', self.env.ref('base.module_category_sales_sales').id)]
    
    sales_price_modifying_group_id = fields.Many2one('res.groups', string='Sale Price Modifying Group', default=_get_group_sale_price_modifying, 
                                                    required=True, domain=_get_group_domain,
                                                    help="Only users who are either in this group or in the groups that inherit this group will be able to modify sales price.")