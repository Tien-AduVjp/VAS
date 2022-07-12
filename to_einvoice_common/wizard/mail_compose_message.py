from odoo import models


class MailComposer(models.TransientModel): 
    _inherit = 'mail.compose.message'
    
    def _get_einvoice_attachment_fields(self):
        """
        Hooking method for other e-invoice provider specific modules to extend for their own specific fields

        :return: invoice's provider specific attachment fields in format of {field: field_name, field: field_name}
        :rtype: dict
        """
        return {}

    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        res = super(MailComposer, self).onchange_template_id(template_id, composition_mode, model, res_id)
        if model == 'account.move':
            account_move = self.env['account.move'].browse([res_id])
            if account_move.exists() \
                and account_move.einvoice_state != 'not_issued' \
                and account_move.type in account_move.get_sale_types() \
                and 'value' in res:
                einvoice_attachment_fields = self._get_einvoice_attachment_fields()
                attachment_vals_list = []
                for field, field_name in einvoice_attachment_fields.items():
                    if hasattr(account_move, field) and hasattr(account_move, field_name):
                        att = getattr(account_move, field)
                        if att:
                            attachment_vals_list.append({
                                'name': getattr(account_move, field_name),
                                'datas': att,
                                'res_model': self._name,
                                'res_id': self.id,
                                })
                if attachment_vals_list:
                    if 'attachment_ids' not in res['value']:
                        res['value']['attachment_ids'] = []
                    attachments = self.env['ir.attachment'].create(attachment_vals_list)
                    res['value']['attachment_ids'] += [(4, attachment.id) for attachment in attachments]
        return res
