# -*- coding: utf-8 -*-

from odoo import models


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    def action_bank_reconcile_bank_statements(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'bank_statement_reconciliation_view',
            'context': {
                'statement_line_ids': self.mapped("line_ids").ids,
                'company_ids': self.mapped('company_id').ids
                },
            }
