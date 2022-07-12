from odoo import models


class MailComposer(models.TransientModel): 
    _inherit = 'mail.compose.message'

    def _get_einvoice_attachment_fields(self):
        res = super(MailComposer, self)._get_einvoice_attachment_fields()
        res.update({
                'sinvoice_representation_zip':'sinvoice_representation_filename_zip'
            })
        return res
