from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    delegation_partner_id = fields.Many2one('res.partner', string='Deletation Partner',
                                            help="The partner on behalf of whom the revenue/expense"
                                            " will be addressed (e.g. Pay/Collect on behalf of Deletation Partner)")

    def _deletation_partner_set_partner(self):
        for r in self:
            if r.delegation_partner_id:
                r.partner_id = r.delegation_partner_id.commercial_partner_id
            else:
                r.partner_id = r.move_id.partner_id.commercial_partner_id

    @api.onchange('delegation_partner_id')
    def _onchange_delegation_partner(self):
        self._deletation_partner_set_partner()
