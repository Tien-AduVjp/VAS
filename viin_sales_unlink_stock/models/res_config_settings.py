from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    prevent_unlink_related_pickings = fields.Boolean(string='Disallow to unlink SO relating Pickings',
                                                    related='company_id.prevent_unlink_related_pickings',
                                                    readonly=False)
