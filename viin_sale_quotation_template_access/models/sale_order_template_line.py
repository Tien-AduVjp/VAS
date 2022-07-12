from odoo import models, api


class SaleOrderTemplateLine(models.Model):
    _inherit = 'sale.order.template.line'
    
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        """
        Problem:
            After installing the 'sale_quotation_builder' module, a user with only 'Access Quotation Template' 
            permission will not be able to create a quote form because there is a related field with model 'product.template' 
            in model 'sale.order.template.line'
        Solution: Use sudo() to grant permission to this user group
        """
        if self.env.user.has_group('viin_sale_quotation_template_access.group_sale_quotation_template_all'):
            self = self.sudo()
        return super(SaleOrderTemplateLine, self).create(vals_list)
    
    def write(self, vals):
        """
        Problem:
            After installing the 'sale_quotation_builder' module, a user with only 'Access Quotation Template' 
            permission will not be able to create a quote form because there is a related field with model 'product.template' 
            in model 'sale.order.template.line'
        Solution: Use sudo() to grant permission to this user group
        """
        if self.env.user.has_group('viin_sale_quotation_template_access.group_sale_quotation_template_all'):
            self = self.sudo()
        return super(SaleOrderTemplateLine, self).write(vals)
