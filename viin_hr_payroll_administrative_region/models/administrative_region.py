from odoo import fields, models


class AdministrativeRegion(models.Model):
    _inherit = 'administrative.region'

    minimum_wage = fields.Monetary(string='Minimum Wage', default=0.0, tracking=True,
                                   groups='viin_administrative_region.group_administrative_region_manager',
                                   help="The minimum wage that is regulated by the state or government")
