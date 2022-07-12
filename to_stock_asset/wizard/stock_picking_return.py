from odoo import models, _
from odoo.exceptions import UserError


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'


    def create_returns(self):
        for line in self.product_return_moves.mapped('move_id.move_line_ids'):
            if line.account_asset_asset_id and line.account_asset_asset_id.state != 'draft':
                raise UserError(_("You cannot return a stock picking that contains assets "
                                  "that has been set to 'Open' state or 'Close' state."))
        return super(ReturnPicking, self).create_returns()
