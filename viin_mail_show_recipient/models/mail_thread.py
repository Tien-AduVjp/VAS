from odoo import models


class MailThread(models.AbstractModel):

    _inherit = 'mail.thread'

    def _notify_classify_recipients(self, recipient_data, model_name, msg_vals=None):
        result = super(MailThread, self)._notify_classify_recipients(recipient_data, model_name, msg_vals)
        partner_ids = []
        for r in result:
            partner_ids.extend(r.get('recipients', []))
        mail_recipients = self.env['res.partner'].sudo().browse(partner_ids).exists().mapped('email_formatted')
        for r in result:
            if r.get('recipients', False):
                r['mail_recipients'] = mail_recipients
        return result
