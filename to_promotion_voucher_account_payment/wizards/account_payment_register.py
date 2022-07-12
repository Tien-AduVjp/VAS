from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    voucher_code = fields.Char(string='Voucher Series')
    voucher_id = fields.Many2one('voucher.voucher', string='Voucher', compute='_compute_voucher_id', store=True)
    voucher_payment = fields.Boolean(string='Is Voucher Payment', compute='_compute_voucher_payment')

    @api.depends('journal_id')
    def _compute_voucher_payment(self):
        for r in self:
            if r.journal_id.voucher_payment:
                r.voucher_payment = True
            else:
                r.voucher_payment = False

    @api.depends('voucher_code')
    def _compute_voucher_id(self):
        vouchers = self.env['voucher.voucher'].search([('serial', 'in', self.mapped('voucher_code')), ('state', 'in', ['activated', 'used'])])
        for r in self:
            if r.voucher_code:
                voucher = vouchers.filtered(lambda v: v.serial == r.voucher_code)
                r.voucher_id = voucher and voucher or False
            else:
                r.voucher_id = False

    def _prepare_payment_vals(self, invoices):
        res = super(AccountPaymentRegister, self)._prepare_payment_vals(invoices)
        if self.employee_id:
            res['voucher_code'] = self.voucher_code
            res['voucher_id'] = self.sudo().voucher_id.id
        return res

    def _reconcile_payments(self, to_process, edit_mode=False):
        if self.voucher_payment:
            domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
            for vals in to_process:
                payment = vals['payment']
                payment_lines = payment.line_ids.filtered_domain(domain)
                lines = vals['to_reconcile']
                for account in payment_lines.account_id:
                    (payment_lines + lines)\
                        .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                        .reconcile()
                unreconciled_lines = payment_lines + lines
                unreconciled_lines.filtered(lambda line: not line.reconciled and line.account_id == payment.destination_account_id)
        else:
            super(AccountPaymentRegister, self)._reconcile_payments(to_process, edit_mode)

    def _create_payment_vals_from_wizard(self):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        res.update({
            'voucher_payment': self.voucher_payment,
            'voucher_code': self.voucher_code,
            'voucher_id': self.sudo().voucher_id.id,
        })
        return res

    def _create_payment_vals_from_batch(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_batch(batch_result)
        res.update({
            'voucher_payment': self.voucher_payment,
            'voucher_code': self.voucher_code,
            'voucher_id': self.sudo().voucher_id.id,
        })
        return res
