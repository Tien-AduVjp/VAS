from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AbstractLoanDisbursementPaymentWizard(models.AbstractModel):
    _name = 'abstract.loan.disbursement.payment.wizard'
    _inherit = 'abstract.loan.payment'
    _description = 'Loan Disbursement Payment Wizard Abstract'

    company_id = fields.Many2one(compute='_compute_company', store=True)

    @api.constrains('disbursement_ids')
    def _check_disbursement_ids(self):
        for r in self:
            company_id = r.disbursement_ids.mapped('company_id')
            if len(company_id) > 1:
                raise ValidationError(_("You cannot make payment for disbursements to multiple companies at once"))
            if self.company_id and self.company_id.id != company_id.id:
                raise ValidationError(_("The payment is for the company '%s' while the matched disbursement(s) belongs to another company (%s)")
                                      % (self.company_id.name, company_id.name))
            partner_id = r.disbursement_ids.mapped('partner_id')
            if len(partner_id) > 1:
                raise ValidationError(_("You cannot make payment for the disbursements that concerning multiple partners"))
            currency_id = r.disbursement_ids.mapped('currency_id')
            if len(currency_id) > 1:
                raise ValidationError(_("You cannot make payment for the disbursements that are in different currencies at once"))

    @api.constrains('disbursement_ids', 'amount')
    def _check_amount_vs_disbursements(self):
        for r in self:
            if not r.disbursement_ids:
                continue

            remaining_amt = r._calculate_remaining_amount()
            if float_compare(r.amount, remaining_amt, precision_rounding=r.currency_id.rounding) == 1:
                raise ValidationError(_("Payment Amount should not be greater than the total remaining amount of the selected disbursement(s)"))

    @api.depends('disbursement_ids.company_id')
    def _compute_company(self):
        for r in self:
            r.company_id = r.disbursement_ids[0].company_id if r.disbursement_ids else False

    def _get_default_disbursements(self):
        active_ids = self.env.context.get('active_ids', [])
        return self.disbursement_ids.search([('id', 'in', active_ids)])

    def _calculate_remaining_amount(self):
        remaining_amt = 0.0
        if self.disbursement_ids:
            remaining_amt = sum(self.disbursement_ids.mapped('to_receive_amount'))
        return remaining_amt

    def _onchange_disbursement_ids(self):
        res = {}
        self.amount = self._calculate_remaining_amount()
        self.communication = ", ".join(self.disbursement_ids.mapped('name'))
        self.partner_id = self.disbursement_ids[0].partner_id if self.disbursement_ids else False
        currency_ids = self.disbursement_ids.mapped('currency_id')
        journal_id_domain = [('type', 'in', ('bank', 'cash'))]
        if currency_ids:
            if any(currency_id.id == self.company_id.currency_id.id for currency_id in currency_ids):
                journal_id_domain += ['|', ('currency_id', '=', False), ('currency_id', 'in', currency_ids.ids)]
            else:
                journal_id_domain += [('currency_id', 'in', currency_ids.ids)]
        res['domain'] = {'journal_id':journal_id_domain}
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.disbursement_ids = self.disbursement_ids.search([('partner_id', '=', self.partner_id.id), ('state', '=', 'confirmed')])

    def action_payment_create_and_match(self):
        self.ensure_one()
        if not self.disbursement_ids:
             raise ValidationError(_("Unable to disburse. Because there are no more loans to disburse"))
        payment_id = self.env['loan.disbursement.payment'].create(self._prepare_payment_data())
        self.disbursement_ids.match_payments(payment_id)
        if payment_id.state == 'matched':
            payment_id.action_post()

    @api.onchange('amount')
    def _onchange_amount(self):
        order_ids = self.disbursement_ids.mapped('order_id')
        while float_compare(self.amount, sum(self.mapped('disbursement_ids.to_receive_amount')), precision_rounding=self.currency_id.rounding) == 1:
            remain_disbursement_ids = order_ids.mapped('disbursement_line_ids').filtered(lambda l: l.id not in self.disbursement_ids.ids and l.state == 'confirmed')
            if not remain_disbursement_ids:
                break
            self.disbursement_ids += remain_disbursement_ids[0]


class LoanBorrowDisbursementPaymentWizard(models.TransientModel):
    _name = 'loan.borrow.disbursement.payment.wizard'
    _inherit = 'abstract.loan.disbursement.payment.wizard'
    _description = 'Loan Borrow Disbursement Payment Wizard'

    disbursement_ids = fields.Many2many('loan.borrow.disbursement', 'loan_borrow_disbursement_payment_wizard_rel', 'wizard_id', 'disbursement_id',
                                        string='Disbursements',
                                        default=lambda self: self._get_default_disbursements())

    @api.onchange('disbursement_ids')
    def _onchange_disbursement_ids(self):
        super(LoanBorrowDisbursementPaymentWizard, self)._onchange_disbursement_ids()


class LoanLendDisbursementPaymentWizard(models.TransientModel):
    _name = 'loan.lend.disbursement.payment.wizard'
    _inherit = 'abstract.loan.disbursement.payment.wizard'
    _description = 'Loan Lend Disbursement Payment Wizard'

    disbursement_ids = fields.Many2many('loan.lend.disbursement', 'loan_lend_disbursement_payment_wizard_rel', 'wizard_id', 'disbursement_id',
                                        string='Disbursements',
                                        default=lambda self: self._get_default_disbursements())

    @api.onchange('disbursement_ids')
    def _onchange_disbursement_ids(self):
        super(LoanLendDisbursementPaymentWizard, self)._onchange_disbursement_ids()
