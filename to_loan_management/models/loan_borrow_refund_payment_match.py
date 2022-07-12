from odoo import models, fields


class LoanBorrowRefundPaymentMatch(models.Model):
    _name = 'loan.borrow.refund.payment.match'
    _inherit = 'abstract.refund.payment.match'
    _description = 'Loan Borrow Refund Payment Match'

    refund_id = fields.Many2one('loan.borrow.refund.line', string='Refund', ondelete='cascade', index=True, required=True)
    disbursement_id = fields.Many2one(related='refund_id.disbursement_id', readonly=True)
    order_id = fields.Many2one(related='refund_id.order_id', store=True, index=True, readonly=True)

    def get_payment_matches_field(self):
        """
        Return the name of the field `loan_borrow_disbursement_payment_match_ids` of the model `loan.disbursement.payment`
        """
        return 'loan_borrow_refund_payment_match_ids'
