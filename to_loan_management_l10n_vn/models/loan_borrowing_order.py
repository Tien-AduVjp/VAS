from odoo import models, api


class LoanBorrowingOrder(models.Model):
    _inherit = 'loan.borrowing.order'

    @api.model
    def _get_default_analytic_tags(self):
        tag_ids = super(LoanBorrowingOrder, self)._get_default_analytic_tags()
        if self.env.user.has_group('analytic.group_analytic_accounting'):
            analytic_tag_id = self.env.ref('l10n_vn_common.account_analytic_tag_borrowing_loan')
            tag_ids.append(analytic_tag_id.id)

        return tag_ids
