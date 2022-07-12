from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_is_zero, float_compare


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    voucher_code = fields.Char(string='Voucher Series')
    voucher_id = fields.Many2one('voucher.voucher', string='Voucher', compute='_compute_voucher_id', store=True)
    voucher_payment = fields.Boolean(string='Is Voucher Payment')

    @api.onchange('journal_id')
    def _onchange_journal(self):
        self.voucher_payment = self.journal_id and self.journal_id.voucher_payment or False
        return super(AccountPayment, self)._onchange_journal()

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        res = super(AccountPayment, self)._onchange_payment_type()
        if not res.get('domain', {}):
            res['domain'] = {}
            res['domain'].setdefault('journal_id', [])
        if self.payment_type != 'inbound' and self.partner_type != 'customer':
            res['domain']['journal_id'].append(('voucher_payment', '=', False))
        return res

    @api.depends('voucher_code')
    def _compute_voucher_id(self):
        for r in self:
            if r.voucher_code:
                voucher = self.env['voucher.voucher'].search([('serial', '=', r.voucher_code), ('state', 'in', ['activated', 'used'])], limit=1)
                r.voucher_id = voucher and voucher or False
            else:
                r.voucher_id = False

    @api.onchange('voucher_code')
    def _onchange_voucher_code(self):
        if self.voucher_code:
            voucher = self.env['voucher.voucher'].search([('serial', '=', self.voucher_code)], limit=1)
            if not voucher:
                raise ValidationError(_('This Voucher code is incorrect. Please re-input another voucher code.'))
            else:
                if voucher.state == 'new':
                    raise ValidationError(_('This Voucher has not been actived. Hence, it cannot be used.'))
                elif voucher.state == 'used' and (voucher.voucher_type_id.payable_once or \
                    float_compare(voucher.used_amount, voucher.value, precision_rounding=self.currency_id.rounding) == 0):
                    raise ValidationError(_("The Voucher '%s' has been used. Please re-input another voucher code.") % (voucher.serial,))
                elif voucher.state == 'expired':
                    raise ValidationError(_('This Voucher is already expired. Please re-input another voucher code.'))
                else:
                    remaining_amount = voucher.value - voucher.used_amount
                    self.amount = self.amount and min(remaining_amount, self.amount) or remaining_amount

    @api.constrains('voucher_id', 'amount')
    def _check_constrains_voucher_id(self):
        for r in self:
            if r.voucher_id:
                if r.voucher_id.state == 'new':
                    raise ValidationError(_('This Voucher has not been actived. Hence, it cannot be used.'))
                elif r.voucher_id.state == 'used' and (r.voucher_id.voucher_type_id.payable_once or \
                    float_compare(r.voucher_id.used_amount, r.voucher_id.value, precision_rounding=r.currency_id.rounding) == 0):
                    raise ValidationError(_("The Voucher '%s' has been used. Please re-input another voucher code.") % (r.voucher_id.serial,))
                elif r.voucher_id.state == 'expired':
                    raise ValidationError(_('This Voucher is already expired. Please re-input another voucher code.'))
                if r.amount and float_compare(r.voucher_id.value, r.amount, precision_digits=2) == -1:
                    raise ValidationError(_('The amount exceeds the voucher \'s value : %s.') % r.voucher_id.value)

    def post(self):
        AccountMove = self.env['account.move'].with_context(default_type='entry')
        for r in self:
            if not r.voucher_id:
                super(AccountPayment, r).post()
            else:
                if r.state != 'draft':
                    raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % r.state)
                if any(inv.state != 'posted' for inv in r.invoice_ids):
                    raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
                if r.partner_type != 'customer' or r.payment_type != 'inbound':
                    raise UserError(_("Promotion voucher payment method is only applicable to payment type 'Receive Money' and partner type 'Customer'"))
                sequence_code = 'account.payment.customer.invoice'
                r.name = self.env['ir.sequence'].with_context(ir_sequence_date=r.payment_date).next_by_code(sequence_code)
                if not r.name:
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
                move = False
                if not float_is_zero(r.voucher_id.price, precision_digits=2):
                    move = AccountMove.create(r._prepare_payment_moves())
                if float_compare(r.voucher_id.price, r.amount, precision_digits=2) != 0:
                    if not move:
                        move = AccountMove.create({'date': r.payment_date,
                                                                'ref': r.communication,
                                                                'journal_id': r.journal_id.id,
                                                                'currency_id': r.journal_id.currency_id.id or r.company_id.currency_id.id,
                                                                'partner_id': r.partner_id.id,})
                    aml_dicts = r._prepare_extra_move_lines(move)
                    amls = self.env['account.move.line']
                    for aml_dict in aml_dicts:
                        amls |= self.env['account.move.line'].with_context(check_move_validity=False).create(aml_dict)
                if r.invoice_ids:
                    (move[0] + r.invoice_ids).line_ids \
                        .filtered(lambda line: not line.reconciled and line.account_id == r.destination_account_id and not (line.account_id == line.payment_id.writeoff_account_id and line.name == line.payment_id.writeoff_label))\
                        .reconcile()
                move.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()
                r.voucher_id.spend(r.amount)
                move_name = self._get_move_name_transfer_separator().join(move.mapped('name'))
                r.write({'state': 'posted', 'move_name': move_name})
                
    def _prepare_extra_move_lines(self, move):
        self.ensure_one()
        move_lines = []
        voucher_accounts = self.voucher_id.product_id.product_tmpl_id._get_product_accounts()
        if float_compare(self.voucher_id.price, self.amount, precision_digits=2) == 1:
            debit_account_id = self.journal_id.default_debit_account_id.id
            credit_account_id = voucher_accounts['voucher_profit'].id
        else:
            debit_account_id = voucher_accounts['voucher_loss'].id
            credit_account_id = self.destination_account_id.id
        amount = abs(self.voucher_id.price - self.amount)
        if not float_is_zero(amount, precision_digits=2):
            move_lines.append({
                                'name': self.name,
                                'move_id': move.id,
                                'partner_id': self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
                                'promotion_voucher_id':self.voucher_id.id,
                                'account_id': credit_account_id,
                                'credit': amount,
                                'payment_id': self.id,
                                })
            move_lines.append({
                                'name': self.name,
                                'move_id': move.id,
                                'partner_id': self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
                                'promotion_voucher_id':self.voucher_id.id,
                                'account_id': debit_account_id,
                                'debit': amount,
                                'payment_id': self.id,
                                })
        return move_lines
    
    def _prepare_payment_moves(self):
        all_move_vals = super(AccountPayment, self)._prepare_payment_moves()
        voucher_payment = self.filtered(lambda p: p.voucher_payment)
        for idx, payment in enumerate(voucher_payment):
            move_vals = all_move_vals[idx]
            company_currency = payment.company_id.currency_id
            counterpart_amount = min(abs(payment.amount), payment.voucher_id.price) * -1
            if payment.currency_id == company_currency:
                balance = counterpart_amount
                counterpart_amount = 0.0
                currency_id = False
            else:
                balance = payment.currency_id._convert(counterpart_amount, company_currency,payment.company_id, payment.payment_date)
                currency_id = payment.currency_id.id
            if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                liquidity_amount = company_currency._convert(
                    balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
            else:
                liquidity_amount = counterpart_amount
            move_vals['line_ids'][0][2].update({'amount_currency': counterpart_amount if currency_id else 0.0,
                                                'credit': -balance,})
            move_vals['line_ids'][1][2].update({'amount_currency': -liquidity_amount if currency_id else 0.0,
                                                'debit': -balance,})
        return all_move_vals
