from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    prevent_unlink_sales_having_invoices = fields.Boolean(related='company_id.prevent_unlink_sales_having_invoices',
                                                          readonly=False)
