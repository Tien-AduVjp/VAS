# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.models import NewId


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    expected_pay_date = fields.Date('Expected Payment Date', help="Expected payment date as manually set through the customer statement (e.g: if you had the customer on the phone and want to remember the date he promised he would pay)")
    internal_note = fields.Text('Internal Note', help="Note you can set through the customer statement about a receivable journal item")
    next_action_date = fields.Date('Next Action Date', help="Date where the next action should be taken for a receivable item. Usually, automatically set when sending reminders through the customer statement.")

    debit_cash_basis = fields.Monetary(currency_field='company_currency_id', compute='_compute_cash_basis', store=True)
    credit_cash_basis = fields.Monetary(currency_field='company_currency_id', compute='_compute_cash_basis', store=True)
    balance_cash_basis = fields.Monetary(compute='_compute_cash_basis', store=True, currency_field='company_currency_id',
        help="Technical field holding the debit_cash_basis - credit_cash_basis in order to open meaningful graph views from reports")

    @api.depends('debit', 'credit', 'currency_id', 'company_currency_id', 'matched_credit_ids', 'matched_debit_ids', 'full_reconcile_id', 'move_id.journal_id')
    def _compute_cash_basis(self):
        # find move lines whose ID is instance of NewID or their move's ID is instance of NewID
        new_id_move_lines = self.filtered(lambda l: isinstance(l.id, NewId) or isinstance(l.move_id.id, NewId))
        remaining = self - new_id_move_lines
        for move_line in new_id_move_lines:
            move_line.update({
                'debit_cash_basis': 0.0,
                'credit_cash_basis': 0.0,
                'balance_cash_basis': 0.0
                })
        matched_percentage_per_move = remaining._get_matched_percentage()
        for move_line in remaining:
            if move_line.journal_id.type in ('sale', 'purchase'):
                move_line.debit_cash_basis = move_line.debit * matched_percentage_per_move.get(move_line.move_id.id, 0.0)
                move_line.credit_cash_basis = move_line.credit * matched_percentage_per_move.get(move_line.move_id.id, 0.0)
            else:
                move_line.debit_cash_basis = move_line.debit
                move_line.credit_cash_basis = move_line.credit
            move_line.balance_cash_basis = move_line.debit_cash_basis - move_line.credit_cash_basis

    def write_blocked(self, blocked):
        """ This function is used to change the 'blocked' status of an aml.
            You need to be able to change it even if the aml is locked by the lock date
            (this function is used in the customer statements) """
        return self.with_context(check_move_validity=False).write({'blocked': blocked})
