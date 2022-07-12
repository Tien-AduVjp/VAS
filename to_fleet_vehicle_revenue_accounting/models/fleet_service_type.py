from odoo import models, fields


class FleetServiceType(models.Model):
    _inherit = 'fleet.service.type'

    product_id = fields.Many2one(help="The product to be used when invoicing vehicle revenues/revenue of this service type")
