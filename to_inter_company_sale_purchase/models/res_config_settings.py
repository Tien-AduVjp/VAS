from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    applicable_on = fields.Selection(related='company_id.applicable_on', readonly=False)
    so_po_auto_validation = fields.Selection(related='company_id.so_po_auto_validation', readonly=False)
