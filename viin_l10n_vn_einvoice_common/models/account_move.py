from odoo import models, _
from odoo.exceptions import AccessError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _prepend_vietnamese_description_to_invoice_lines(self):
        self.filtered(lambda move: move.einvoice_state == 'not_issued'
                                   and move.type in ('out_invoice', 'out_refund')
                      ).invoice_line_ids._prepend_vietnamese_description_to_name()

    def action_prepend_vietnamese_description_to_invoice_lines(self):
        if not self.env.user.has_group('account.group_account_invoice'):
            group = self.env.ref('account.group_account_invoice')
            raise AccessError(_("Only users in the group %s can do this action") % group.display_name)
        self._prepend_vietnamese_description_to_invoice_lines()
