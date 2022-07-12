from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dedicate_apps_store = fields.Boolean(related='website_id.dedicate_apps_store', readonly=False)
