from odoo import fields, models


class MrpConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    manufacturing_period = fields.Selection(string='Manufacturing Period',
                                            related='company_id.manufacturing_period',
                                            default='month', readonly=False)
    manufacturing_period_to_display = fields.Integer(string='Number of Period Columns',
                                                     related='company_id.manufacturing_period_to_display',
                                                     default=12, readonly=False)
