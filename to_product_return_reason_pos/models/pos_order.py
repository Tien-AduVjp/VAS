from odoo import models, api, _
from odoo.tools import float_is_zero


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _prepare_order_line(self, order):
        order_lines = []
        invalid_product = []
        return_value = {}
        for line in order['lines']:
            if line['return_reason_id'] == '-1':
                if line['new_return_reason']:
                    return_reason_id = self.env['product.return.reason'].search([('name', '=', line['new_return_reason'])])
                    if not return_reason_id:
                        return_reason_id = self.env['product.return.reason'].create({'name': line['new_return_reason']})
                    line['return_reason_id'] = return_reason_id.id or None
                else:
                    line['return_reason_id'] = None
            product_id = self.env['product.product'].browse(int(line['product_id']))
            if not product_id.pos_returnable:
                invalid_product.append(product_id.id)
                continue
            tax_ids = []
            if line['tax_ids']:
                tax_ids = [int(i) for i in line['tax_ids'].split(',')]
            order_lines.append({
                    'product_id': line['product_id'],
                    'qty': line['qty'],
                    'price_unit': line['price_unit'],
                    'discount': line['discount'],
                    'return_reason_id': line['return_reason_id'],
                    'price_subtotal': line['price_subtotal'],
                    'price_subtotal_incl': line['price_subtotal_incl'],
                    'tax_ids': [(6, 0, tax_ids)]
            })
        return_value['invalid_product'] = invalid_product
        return_value['order_lines'] = order_lines
        return return_value
    
    def _default_session(self):
        return self.env['pos.session'].search([('state', '=', 'opened'), ('user_id', '=', self.env.uid)], limit=1)
    
    @api.model
    def create_return_order_from_ui(self, order):
        picking_type = self._default_session().config_id.picking_type_id
        order_lines = self._prepare_order_line(order)
        res = {}
        if picking_type:
            if picking_type.return_reason_required:
                for line in order_lines['order_lines']:
                    product = self.env['product.product'].browse(int(line['product_id']))
                    if not line['return_reason_id'] and not float_is_zero(float(line['qty']), precision_rounding=product.uom_id.rounding):
                        res['invalid_order'] = 1
                        res['invalid_product'] = []
                        res['order_id'] = 0
                        res['order_error'] = _("The operation '%s' requires Return Reason. Please specify one.") % (picking_type.display_name,)
                        return res
        res = super(PosOrder, self).create_return_order_from_ui(order)
        res['invalid_order'] = 0
        return res

    def action_pos_order_paid(self):
        res = super(PosOrder, self).action_pos_order_paid()
        for r in self:
            return_reason_ids = r.lines.mapped('return_reason_id')
            if r.picking_id and return_reason_ids:
                r.picking_id.return_reason_ids = return_reason_ids
        return res

    def create_picking(self):
        res = super(PosOrder, self).create_picking()
        Move = self.env['stock.move']
        for order in self:
            if not order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                continue
            for line in order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_rounding=l.product_id.uom_id.rounding)):
                if line.return_reason_id:
                    move = Move.search([('product_id', '=', line.product_id.id), ('picking_id', '=', order.picking_id.id)])
                    if move:
                        move.return_reason_id = line.return_reason_id.id
        return res
