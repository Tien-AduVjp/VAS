from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _get_default_hbd_email_template_id(self):
        return self.env.ref('to_partner_dob_send_email.email_template_partner_happy_birthday', False)

    send_hbd_email = fields.Boolean(string='Send Happy Birthday Email', default=True)
    hdb_email_template_id = fields.Many2one('mail.template', string="Happy Birthday Email Template", default=_get_default_hbd_email_template_id)
