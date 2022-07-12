from odoo import models, fields


class LoanBorrowDisbursementPaymentMatch(models.Model):
    _name = 'loan.borrow.disbursement.payment.match'
    _inherit = 'abstract.disbursement.payment.match'
    _description = 'Loan Borrow Disbursement Payment Match'

    disbursement_id = fields.Many2one('loan.borrow.disbursement', string='Disbursement', ondelete='cascade', index=True, required=True)
    order_id = fields.Many2one(related='disbursement_id.order_id', store=True, index=True, readonly=True)

    def get_payment_matches_field(self):
        """
        Return the name of the field `loan_borrow_disbursement_payment_match_ids` of the model `loan.disbursement.payment`
        """
        return 'loan_borrow_disbursement_payment_match_ids'
