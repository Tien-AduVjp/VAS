from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    loyalty_id = fields.Many2one('loyalty.program', string='Loyalty Program for the Point of Sale', help='The loyalty program used by this point_of_sale')

    @api.constrains('loyalty_id', 'journal_id', 'company_id')
    def _check_journal_currency_vs_loyalty_program(self):
        for r in self:
            if not r.loyalty_id:
                continue
            loyalty_currency_id = r.loyalty_id.currency_id or r.company_id.currency_id
            if r.journal_id:
                pos_currency_id = r.journal_id.currency_id or r.journal_id.company_id.currency_id
            else:
                pos_currency_id = self.env.company.currency_id

            if loyalty_currency_id != pos_currency_id:
                raise ValidationError(_("Currency discrepancy between the PoS '%s' and the loyalty program '%s'") % (r.name, r.loyalty_id.name))
