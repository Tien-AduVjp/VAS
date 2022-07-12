from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    balance_carry_forward_journal_id = fields.Many2one('account.journal', string="Balance Carry Forward Journal",
                                                       help="The journal that stores account balance carry forward journal entries")

    def _prepare_balance_carry_forward_journal_data(self):
        self.ensure_one()
        return {
            'name': _('Balance Carry Forward Journal'),
            'code': 'BCF',
            'type': 'general',
            'company_id': self.id,
            'show_on_dashboard': False,
            }

    def _generate_balance_carry_forward_journal_if_not_exists(self):
        Journal = self.env['account.journal'].sudo()
        vals_list = []
        for r in self:
            journal_id = Journal.search([('code', '=', 'BCF'), ('company_id', '=', r.id)], limit=1)
            if not journal_id:
                vals_list.append(r._prepare_balance_carry_forward_journal_data())
        if vals_list:
            Journal.create(vals_list)

    def _assign_balance_carry_forward_journal(self):
        self._generate_balance_carry_forward_journal_if_not_exists()
        for r in self:
            journal_id = self.env['account.journal'].search([('code', '=', 'BCF'), ('company_id', '=', r.id)], limit=1)
            r.balance_carry_forward_journal_id = journal_id.id
