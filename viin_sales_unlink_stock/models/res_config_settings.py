from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    prevent_unlink_sales_having_pickings = fields.Boolean(related='company_id.prevent_unlink_sales_having_pickings',
                                                          readonly=False)
