from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    unique_doc_name = fields.Boolean(related="company_id.unique_doc_name", readonly=False)
