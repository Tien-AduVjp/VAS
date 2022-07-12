from odoo import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('asset_category_id')
    def _onchange_asset_category_id(self):
        res = super(AccountMoveLine, self)._onchange_asset_category_id()

        asset_category = self.asset_category_id.sudo()
        if self.move_id.move_type == 'in_invoice' and asset_category:
            analytic_tags = asset_category.analytic_tag_ids
            remain_tag_ids = set(analytic_tags.ids) - set(self.analytic_tag_ids.ids)
            if remain_tag_ids:
                self.analytic_tag_ids = [(4, tag_id) for tag_id in remain_tag_ids]
            else:
                self.analytic_tag_ids = False
        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()

        for r in self:
            asset_category = r.product_id.sudo().asset_category_id
            if asset_category:
                analytic_tags = asset_category.analytic_tag_ids
                if analytic_tags:
                    remain_tag_ids = set(analytic_tags.ids) - set(r.analytic_tag_ids.ids)
                    if remain_tag_ids:
                        r.analytic_tag_ids = [(4, tag_id) for tag_id in remain_tag_ids]
                else:
                    r.analytic_tag_ids = False
        return res
