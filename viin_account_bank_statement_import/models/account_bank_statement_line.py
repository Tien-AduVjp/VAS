# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    # Ensure transactions can be imported only once (if the import format provides unique transaction ids)
    unique_import_id = fields.Char(string='Import ID', readonly=True, copy=False)

    _sql_constraints = [
        ('unique_import_id', 'unique (unique_import_id)', 'A bank account transactions can be imported only once !')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountBankStatementLine, self).create(vals_list)
        for r in res:
            if not r.partner_bank_id and r.account_number:
                # Fill the partner and his bank account or create the bank account
                partner_bank = self.env['res.partner.bank'].search([
                    ('acc_number', '=', r.account_number),
                    '|', ('company_id', '=', False),
                         ('company_id', '=', r.statement_id.company_id.id)], limit=1)
                if partner_bank:
                    r.move_id.write({
                        'partner_bank_id': partner_bank.id,
                        'partner_id': partner_bank.partner_id.id,
                    })
        return res
