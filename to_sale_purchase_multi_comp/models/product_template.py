from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_to_purchase = fields.Boolean(company_dependent=True)
