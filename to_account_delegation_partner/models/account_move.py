from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        self.line_ids._deletation_partner_set_partner()
        return res

