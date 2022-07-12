# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'to.vietnamese.number2words']

    no_of_origin = fields.Char(string='No. of Origin', size=256,
                                  help="Number of the origin documents (e.g. Purchase Voucher number, Invoice Number, etc), to be displayed on the PDF printed version of this document.")
    recipient_payer = fields.Char(string='Recipient / Payer', size=256, compute='_get_recipient_payer', readonly=False, store=True,
                                  help='The name of the person who pay/receive the payment. If empty, the corresponding partner name will be used instead.')

    total_in_word = fields.Char(string='In words', compute='_compute_num2words')

    def _compute_num2words(self):
        for r in self:
            r.total_in_word = r.num2words(r.amount, precision_rounding=r.currency_id.rounding)
    
    @api.depends('partner_id')
    def _get_recipient_payer(self):
        for r in self:
            if r.partner_id and r.partner_id.company_type == 'person':
                r.recipient_payer = r.partner_id.name
            else:
                r.recipient_payer = False
