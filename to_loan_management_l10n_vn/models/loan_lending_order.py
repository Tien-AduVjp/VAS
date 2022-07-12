from odoo import models, api


class LendingLoanOrder(models.Model):
    _inherit = 'loan.lending.order'

    @api.model
    def _get_default_analytic_tags(self):
        tag_ids = super(LendingLoanOrder, self)._get_default_analytic_tags()
        if self.env.user.has_group('analytic.group_analytic_accounting'):     
            analytic_tag_id = self.env.ref('l10n_vn_c200.analytic_tag_interests_dividends_distributed_profits')
            tag_ids.append(analytic_tag_id.id)
        return tag_ids
