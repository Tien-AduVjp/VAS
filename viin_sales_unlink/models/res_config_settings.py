from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    prevent_unlink_related_invoices = fields.Boolean(string='Disallow to unlink SO/SO line relating Invoices',
                                                    related='company_id.prevent_unlink_related_invoices',
                                                    readonly=False)
