from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError


class Wallet(models.Model):
    _inherit = 'wallet'

    adjustment_move_ids = fields.Many2many('account.move', compute='_compute_adjustment_moves', groups="account.group_account_invoice")
    adjustment_moves_count = fields.Integer(compute='_compute_adjustment_moves', groups="account.group_account_invoice")

    @api.depends('move_line_ids.is_wallet_adjustment')
    def _compute_adjustment_moves(self):
        adjustment_move_lines = self.env['account.move.line'].search([
            ('is_wallet_adjustment', '=', True),
            ('wallet_id', 'in', self.ids)
        ])
        for r in self:
            r.adjustment_move_ids = adjustment_move_lines.filtered(lambda l: l.wallet_id == r).mapped('move_id')
            r.adjustment_moves_count = len(r.adjustment_move_ids)

    def _adjust(self, amount, journal):
        self.ensure_one()
        if not self.env.user.has_group('account.group_account_manager'):
            raise AccessError(_('You do not have permission to do this action. Only Account Manager can do it!'))
        if not journal.default_debit_account_id:
            raise ValidationError(_('Please setup default debit account for the journal %s') % journal.name)
        if not journal.default_credit_account_id:
            raise ValidationError(_('Please setup default credit account for the journal %s') % journal.name)
        if not amount or self.currency_id.is_zero(amount):
            raise ValidationError(_('Wallet adjustment amount is invalid'))
        vals = self._prepare_adjustment_move_vals(amount, journal)
        move = self.env['account.move'].create(vals)
        move.post()
        return move

    def _prepare_adjustment_move_vals(self, amount, journal):
        self.ensure_one()
        date = self._context.get('force_period_date', fields.Date.context_today(self))
        company_id = self._context.get('force_company', self._context.get('default_company_id', self.env.company.id))
        company = self.env['res.company'].browse(company_id)
        wallet_total = amount
        if self.currency_id == company.currency_id:
            currency_id = False
            amount_currency = 0.0
        else:
            currency_id = self.currency_id.id
            amount_currency = amount
            amount = self.currency_id._convert(amount_currency, company.currency_id, company, date=date)
        return {
            'ref': 'WALLET-%s-ADJUSTMENT' % self.id,
            'journal_id': journal.id,
            'wallet_total': wallet_total,
            'currency_id': self.currency_id.id,
            'date': date,
            'line_ids': [
                (0, 0, {
                    'account_id': journal.default_debit_account_id.id if amount > 0.0 else journal.default_credit_account_id.id,
                    'partner_id': self.partner_id.commercial_partner_id.id,
                    'debit': amount if amount > 0.0 else 0.0,
                    'credit': -amount if amount < 0.0 else 0.0,
                    'currency_id': currency_id,
                    'amount_currency': amount_currency
                }),
                (0, 0, {
                    'account_id': self.partner_id.commercial_partner_id.property_account_receivable_id.id,
                    'partner_id': self.partner_id.commercial_partner_id.id,
                    'debit': -amount if amount < 0 else 0.0,
                    'credit': amount if amount > 0 else 0.0,
                    'currency_id': currency_id,
                    'amount_currency': -amount_currency,
                    'wallet': True,
                    'wallet_id': self.id,
                    'wallet_amount': amount,
                    'wallet_amount_currency': amount_currency,
                    'is_wallet_adjustment': True
                })
            ]
        }

    def action_view_adjustment_moves(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_journal_line').read()[0]
        # override the context to get rid of the default filtering
        action['context'] = {}
        action['domain'] = [('id', 'in', self.adjustment_move_ids.ids)]
        return action
