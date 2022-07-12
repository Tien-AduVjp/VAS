import threading

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    return_reason_id = fields.Many2one('product.return.reason', string='Return Reason', ondelete='restrict')

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = super(ReturnPicking, self)._prepare_move_default_values(return_line, new_picking)
        if return_line.return_reason_id:
            vals['return_reason_id'] = return_line.return_reason_id.id
        return vals

    def _create_returns(self):
        new_picking_id, picking_type_id = super(ReturnPicking, self)._create_returns()

        if picking_type_id:
            picking_type = self.env['stock.picking.type'].browse(picking_type_id)
            if picking_type.return_reason_required:
                for line in self.product_return_moves:
                    if not line.return_reason_id:
                        raise UserError(_("The operation '%s' requires Return Reason. Please specify one.")
                                        % (picking_type.display_name,))

        return new_picking_id, picking_type_id

    def create_returns(self):
        res = super(ReturnPicking, self).create_returns()
        res['context'].update({'search_default_return_reason_id': False})
        return res
