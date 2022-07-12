from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_is_zero, float_compare
from odoo.osv import expression


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    voucher_code = fields.Char(string='Voucher Series')
    voucher_id = fields.Many2one('voucher.voucher', string='Voucher', compute='_compute_voucher_id', store=True)
    voucher_payment = fields.Boolean(string='Is Voucher Payment')

    @api.onchange('journal_id')
    def _onchange_journal(self):
        self.voucher_payment = self.journal_id and self.journal_id.voucher_payment or False
        return super(AccountPayment, self)._onchange_journal()

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

    @api.constrains('voucher_id', 'amount', 'payment_type', 'partner_type')
    def _check_constrains_voucher_id(self):
        for r in self:
            if r.sudo().voucher_id:
                if r.voucher_id.state == 'new':
                    raise ValidationError(_('This Voucher has not been actived. Hence, it cannot be used.'))
                elif r.voucher_id.state == 'used' and (r.voucher_id.voucher_type_id.payable_once or \
                    float_compare(r.voucher_id.used_amount, r.voucher_id.value, precision_rounding=r.currency_id.rounding) == 0):
                    raise ValidationError(_("The Voucher '%s' has been used. Please re-input another voucher code.") % (r.voucher_id.serial,))
                elif r.voucher_id.state == 'expired':
                    raise ValidationError(_('This Voucher is already expired. Please re-input another voucher code.'))
                if r.amount and float_compare(r.voucher_id.value, r.amount, precision_digits=2) == -1:
                    raise ValidationError(_('The amount exceeds the voucher \'s value : %s.') % r.voucher_id.value)
                if r.partner_type != 'customer' or r.payment_type != 'inbound':
                    raise UserError(_("Promotion voucher payment method is only applicable to payment type 'Receive Money' and partner type 'Customer'"))

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)
        if self.voucher_payment and self.sudo().voucher_id:
            if not self.currency_id.is_zero(self.voucher_id.price):
                company_currency = self.company_id.currency_id
                counterpart_amount = min(abs(self.amount), self.voucher_id.price) * -1
                if self.currency_id == company_currency:
                    balance = counterpart_amount
                    counterpart_amount = 0.0
                    currency_id = False
                else:
                    balance = self.currency_id._convert(
                        counterpart_amount, company_currency, self.company_id, self.date
                    )
                    currency_id = self.currency_id.id
                if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
                    liquidity_amount = company_currency._convert(
                        balance, self.journal_id.currency_id, self.company_id, self.date
                    )
                else:
                    liquidity_amount = counterpart_amount
                res[0].update({
                    'debit':-balance
                })
                res[1].update({
                    'credit':-balance
                })
                if currency_id:
                    res[0].update({
                        'amount_currency':-liquidity_amount,
                    })
                    res[1].update({
                        'amount_currency': counterpart_amount,
                    })
            if float_compare(self.voucher_id.price, self.amount, precision_rounding=self.currency_id.rounding) != 0:
                voucher_accounts = self.voucher_id.product_id.product_tmpl_id._get_product_accounts()
                if float_compare(self.voucher_id.price, self.amount, precision_rounding=self.currency_id.rounding) == 1:
                    debit_account_id = self.company_id.property_unearn_revenue_account_id.id
                    credit_account_id = voucher_accounts['voucher_profit'].id
                else:
                    debit_account_id = voucher_accounts['voucher_loss'].id
                    credit_account_id = self.destination_account_id.id
                amount = abs(self.voucher_id.price - self.amount)
                if not self.currency_id.is_zero(amount):
                    res.append({
                        'partner_id': self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
                        'promotion_voucher_id':self.voucher_id.id,
                        'account_id': debit_account_id,
                        'debit': amount,
                    })
                    res.append({
                        'partner_id': self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
                        'promotion_voucher_id':self.voucher_id.id,
                        'account_id': credit_account_id,
                        'credit': amount,
                    })
        return res

    def _get_multi_line_payment_domain(self):
        res = super(AccountPayment, self)._get_multi_line_payment_domain()
        return expression.OR([res, [('voucher_payment', '!=', False), ('voucher_id', '!=', False)]])

    def action_post(self):
        for r in self:
            if r.sudo().voucher_id:
                r.voucher_id.spend(r.amount)
        return super(AccountPayment, self).action_post()
