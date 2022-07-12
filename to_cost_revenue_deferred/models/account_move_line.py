from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    deferral_id = fields.Many2one('cost.revenue.deferral', string="Deferral", ondelete='restrict')

    def _get_deferral_analytic_tags_from_deferral_categ(self):
        if self.move_id.move_type in('in_invoice', 'in_refund'):
            analytic_tag_ids = self.product_id._get_deferral_analytic_tags(deferral_type='cost')
        else:
            analytic_tag_ids = self.product_id._get_deferral_analytic_tags(deferral_type='revenue')
        return analytic_tag_ids

    def _get_deferral_analytic_account_from_deferral_categ(self):
        if self.move_id.move_type in('in_invoice', 'in_refund'):
            account_analytic_id = self.product_id._get_deferral_analytic_account(deferral_type='cost')
        else:
            account_analytic_id = self.product_id._get_deferral_analytic_account(deferral_type='revenue')
        return account_analytic_id

    def _get_deferral_account_from_deferral_categ(self):
        if self.move_id.move_type in('in_invoice', 'in_refund'):
                return self.product_id.cost_deferral_category_id.deferred_account_id
        return self.product_id.revenue_deferral_category_id.deferred_account_id

    def _get_deferral_account(self):
        return self._get_deferral_account_from_deferral_categ()

    def _get_deferral_analytic_tags(self):
        return self._get_deferral_analytic_tags_from_deferral_categ()

    def _get_deferral_analytic_account(self):
        return self._get_deferral_analytic_account_from_deferral_categ()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        for r in self:
            if r.product_id.revenue_deferral_category_id or r.product_id.cost_deferral_category_id:
                account_id = r._get_deferral_account()
                if account_id:
                    r.account_id = account_id
                r.analytic_tag_ids = r._get_deferral_analytic_tags()
                r.analytic_account_id = r._get_deferral_analytic_account()
        return res
