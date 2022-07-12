from odoo import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        for r in self:
            if r.move_id.move_type in ('out_invoice', 'out_refund'):
                analytic_tag_id = self.env.ref('l10n_vn_common.account_analytic_tag_interests_dividends_distributed_profits')
            else:
                analytic_tag_id = self.env.ref('l10n_vn_common.account_analytic_tag_borrowing_loan')

            if r.product_id and r.product_id.is_loan:
                if analytic_tag_id:
                    r.analytic_tag_ids = [(4, analytic_tag_id.id)]
            else:
                remain_tags = r.analytic_tag_ids - analytic_tag_id
                if remain_tags:
                    r.analytic_tag_ids = [(4, tag_id) for tag_id in remain_tags.ids]
                else:
                    r.analytic_tag_ids = False
        return res
