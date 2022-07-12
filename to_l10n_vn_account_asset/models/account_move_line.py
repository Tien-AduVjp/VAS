from odoo import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('asset_category_id')
    def _onchange_asset_category_id(self):
        super(AccountMoveLine, self)._onchange_asset_category_id()
        if self.move_id.type == 'in_invoice':
            fixed_asset_analytic_tag_id = self.env.ref('l10n_vn_c200.analytic_tag_fixed_assets')
            if self.asset_category_id:
                self.analytic_tag_ids = [(4, fixed_asset_analytic_tag_id.id)]
            else:
                remain_tag_ids = set(self.analytic_tag_ids.ids) - set(fixed_asset_analytic_tag_id.ids)
                if remain_tag_ids:
                    self.analytic_tag_ids = [(4, tag_id) for tag_id in remain_tag_ids]
                else:
                    self.analytic_tag_ids = False

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        fixed_asset_analytic_tag_id = self.env.ref('l10n_vn_c200.analytic_tag_fixed_assets')
        for r in self:
            if r.product_id and r.product_id.asset_category_id:
                if fixed_asset_analytic_tag_id:
                    r.analytic_tag_ids = [(4, fixed_asset_analytic_tag_id.id)]
            else:
                remain_tag_ids = set(r.analytic_tag_ids.ids) - set(fixed_asset_analytic_tag_id.ids)
                if remain_tag_ids:
                    r.analytic_tag_ids = [(4, tag_id) for tag_id in remain_tag_ids]
                else:
                    r.analytic_tag_ids = False
        return res
