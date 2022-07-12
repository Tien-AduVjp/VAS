from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError


class AbstractLoanLine(models.AbstractModel):
    _name = 'abstract.loan.line'
    _inherit = ['loan.mixin', 'mail.thread']
    _description = 'Loan Line Abstract'

    amount = fields.Monetary(string='Amount', required=True, readonly=False, states={'confirmed': [('readonly', True)],
                                                                                     'paid': [('readonly', True)]})
    partner_id = fields.Many2one('res.partner', string='Partner')
    date = fields.Date(string='Date', compute='_compute_date', inverse='_set_date', store=True,
                       readonly=False, states={'confirmed': [('readonly', True)],
                                               'paid': [('readonly', True)]},
                       help="The magic date which is either Full Payment Date or Due Date or Date Confirmed which is available first")
    first_payment_date = fields.Date(string='First Payment Date', compute='_compute_payment_date', store=True)
    last_payment_date = fields.Date(string='Last Payment Date', compute='_compute_payment_date', store=True)
    full_payment_date = fields.Date(string='Full Payment Date', compute='_compute_payment_date', store=True)

    @api.constrains('amount')
    def _check_amount(self):
        for r in self:
            if float_is_zero(r.amount, precision_rounding=r.currency_id.rounding):
                raise UserError(_("Zero amount makes no sense. Please input a none zero amount."))

    @api.depends('full_payment_date', 'date_maturity', 'date_confirmed')
    def _compute_date(self):
        for r in self:
            r.date = r.full_payment_date or r.date_maturity or r.date_confirmed

    def _set_date(self):
        pass

    @api.depends('state', 'payment_ids', 'payment_ids.payment_date')
    def _compute_payment_date(self):
        for r in self:
            if not r.payment_ids:
                r.first_payment_date = False
                r.full_payment_date = False
            else:
                r.first_payment_date = r.payment_ids[0].payment_date
                last_payment_date = r.payment_ids[-1].payment_date
                r.last_payment_date = last_payment_date
                if r.state == 'paid':
                    r.full_payment_date = last_payment_date
                else:
                    r.full_payment_date = False

    def get_payment_dates(self):
        """
        This method to return a list of payment dates. In case no payment date, maturity date will be return
        @rtype: list
        @return: a list of date strings 
        """
        payment_dates = []
        for r in self:
            if not r.payment_ids:
                if not r.date:
                    raise UserError(_("You should set date for Disbursement Plan Line (%s) before doing next actions") % (r.display_name))
                payment_dates.append(r.date)
            else:
                payment_dates += r.payment_ids.mapped('payment_date')
        payment_dates.sort()
        return payment_dates

