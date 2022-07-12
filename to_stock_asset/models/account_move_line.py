from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    asset_category_id = fields.Many2one(help="If set, it will automatically generate the corresponding assets if Product Type as Service / Consumable.")

    def _prepare_asset_vals_list(self):
        self = self.filtered(lambda line: line.product_id.type != 'product')
        return super(AccountMoveLine, self)._prepare_asset_vals_list()
