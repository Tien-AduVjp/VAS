from odoo import models, fields, api


class LoanBorrowDisbursement(models.Model):
    _name = 'loan.borrow.disbursement'
    _description = 'Disbursement Plan Line'
    _inherit = 'abstract.loan.disbursement'

    order_id = fields.Many2one('loan.borrowing.order', string='Contract', required=True,
                               readonly=False, states={'confirmed': [('readonly', True)],
                                                       'paid': [('readonly', True)],
                                                       'refunded': [('readonly', True)],
                                                       'cancelled': [('readonly', True)]},
                               help="The Borrowing Loan contract that the disbursement follows")
    partner_id = fields.Many2one(related='order_id.partner_id', store=True, readonly=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, readonly=True)
    company_id = fields.Many2one(related='order_id.company_id', store=True, readonly=True)
    journal_id = fields.Many2one(related='order_id.journal_id', readonly=True)
    account_id = fields.Many2one(related='order_id.account_id', readonly=True)

    refund_line_ids = fields.One2many('loan.borrow.refund.line', 'disbursement_id',
                                  string='Refunds',
                                  help="The principal refund that schedules refund for this disbursement")
    interest_line_ids = fields.One2many('loan.borrow.interest.line', 'disbursement_id', string='Interests',
                                        help="The scheduled interests concerning to this disbursement")

    payment_match_ids = fields.One2many('loan.borrow.disbursement.payment.match', 'disbursement_id', string='Payment Matches', readonly=True)
    payment_ids = fields.Many2many('loan.disbursement.payment', 'disbursement_payment_borrow_disbursement_rel', 'disbursement_id', 'payment_id',
                                   string='Payments', compute='_compute_payment_ids', store=True)
    move_ids = fields.Many2many('account.move', 'acc_move_borrow_disbursement_rel', 'disbursement_id', 'move_id',
                                string="Journal Entries", compute='_compute_move_ids', store=True)

    @api.depends('payment_match_ids.payment_id')
    def _compute_payment_ids(self):
        for r in self:
            r.payment_ids = r.payment_match_ids.mapped('payment_id')

    @api.depends('payment_ids.move_id')
    def _compute_move_ids(self):
        for r in self:
            r.move_ids = r.payment_ids.mapped('move_id')

    def _get_sequence(self):
        return self.env['ir.sequence'].next_by_code('loan.borrowing.disbursement') or '/'

    def _get_refund_line_model(self):
        return 'loan.borrow.refund.line'

    def _get_loan_interest_line_model(self):
        return 'loan.borrow.interest.line'

    def _get_payment_match_model(self):
        return 'loan.borrow.disbursement.payment.match'

    def _get_disbursement_payment_action_xml_id(self):
        return 'to_loan_management.action_loan_borrow_disbursement_payment_wizard'
