from odoo import api, models, fields, _
from odoo.exceptions import UserError

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _prepare_order_to_create(self, return_order_data, order_lines):
        return {
            'partner_id': return_order_data['partner_id'],
            'date_order': fields.Datetime.now(),
            'user_id': return_order_data['user_id'],
            'pos_reference': return_order_data['pos_reference'],
            'state': 'draft',
            'session_id': return_order_data['session_id'],
            'fiscal_position_id': return_order_data['fiscal_position_id'],
            'refund_original_order_id': return_order_data['refund_original_order_id'],
            'lines': [(0, 0, line) for line in order_lines],
            'amount_paid': 0.0,
            'amount_total': 0.0,
            'amount_tax': 0.0,
            'amount_return': 0.0
            }

    def _prepare_order_line(self, return_order_data):
        order_lines = []
        invalid_product = []
        return_value = {}
        for line in return_order_data['lines']:
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
                    'tax_ids': [(6, 0, tax_ids)],
                    'price_subtotal': line['price_subtotal_incl'],
                    'price_subtotal_incl': line['price_subtotal']
            })
        return_value['invalid_product'] = invalid_product
        return_value['order_lines'] = order_lines
        return return_value

    @api.model
    def create_return_order_from_ui(self, return_order_data):
        """
        create a return order from the point of sale UI.
        """
        return_value = {}
        order_lines = self._prepare_order_line(return_order_data)
        if order_lines['invalid_product']:
            return_value['invalid_product'] = order_lines['invalid_product']
            return_value['order_id'] = 0
            return return_value

        new_order = self._prepare_order_to_create(return_order_data, order_lines['order_lines'])
        order = self.create(new_order)
        order._onchange_amount_all()
        return_value['invalid_product'] = order_lines['invalid_product']
        return_value['order_id'] = order.id
        return return_value

    @api.model
    def onchange_qty_from_ui(self, line):
        product_id = self.env['product.product'].browse(int(line['product_id']))
        order_id = self.browse(int(line['order_id']))
        if order_id and product_id:
            if not order_id.pricelist_id:
                raise UserError(_('You have to select a pricelist in the sale form !'))
            price = float(line['price_unit']) * (1 - (float(line['discount']) or 0.0) / 100.0)
            price_subtotal = price_subtotal_incl = price * float(line['qty'])
            if (product_id.taxes_id):
                taxes = product_id.taxes_id.compute_all(price, order_id.pricelist_id.currency_id, float(line['qty']), product=product_id, partner=False)
                price_subtotal = taxes['total_excluded']
                price_subtotal_incl = taxes['total_included']
            return [price_subtotal, price_subtotal_incl]

        return []

    def test_paid(self):
        """A Point of Sale is paid when the sum
        @return: True
        """
        for order in self:
            if order.lines and not order.amount_total:
                continue
            if not order.lines or not order.payment_ids or not order.pricelist_id.currency_id.is_zero(order.amount_total - order.amount_paid):
                return False
        return True
    
    @api.model
    def create_payment_from_ui(self, payment):
        """Payment order from the point of sale ui.
         """
        order_id = self.browse(int(payment['order_id']))
        data = {
                #'name': payment['payment_name'] and payment['payment_name'] or '',
                'payment_date': fields.Datetime.now(),
                'amount': float(payment['amount']),
                'payment_method_id': int(payment['journal_id']),
                'pos_order_id': int(payment['order_id']),
                }
        order_id.add_payment(data)
        if order_id.test_paid():
            order_id.action_pos_order_paid()
        return True
