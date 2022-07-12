from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    send_hbd_email = fields.Boolean(related='company_id.send_hbd_email', readonly=False)
    hdb_email_template_id = fields.Many2one(string="Happy Birthday Email Template", related='company_id.hdb_email_template_id', readonly=False)
