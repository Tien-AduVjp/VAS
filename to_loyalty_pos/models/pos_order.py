from odoo import api, fields, models
from odoo.tools import float_is_zero
from odoo.tools.float_utils import float_round


class PosOrder(models.Model):
    _inherit = 'pos.order'

    loyalty_points = fields.Float(string='Loyalty Points', help="The amount of Loyalty points the customer won or lost with this order")

    @api.model
    def _order_fields(self, ui_order):
        fields = super(PosOrder, self)._order_fields(ui_order)
        fields['loyalty_points'] = ui_order.get('loyalty_points', 0)
        return fields

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrder, self).create_from_ui(orders, draft)
        prec = self.env['decimal.precision'].precision_get('Loyalty')
        ord_ids = []
        for order in order_ids:
            ord_ids.append(order['id'])
        vals_list = []
        for ord in self.browse(ord_ids):
            for line in ord.lines:
                if not float_is_zero(line.loyalty_points, precision_digits=prec):
                    vals_list.append(line._prepare_loyalty_point_data())
            if not float_is_zero(ord.config_id.loyalty_id.pp_order, precision_digits=prec):
                vals_list.append({
                    'name': ord.name,
                    'partner_id': ord.partner_id.id,
                    'points': float_round(ord.config_id.loyalty_id.pp_order, precision_digits=prec),
                    'loyalty_program_id': ord.config_id.loyalty_id.id,
                    'date_order': ord.date_order,
                    'salesperson_id': ord.user_id.id,
                    'manual_adjustment': False,
                    'pos_order_id': ord.id,
                })
        if vals_list:
            self.env['loyalty.point'].create(vals_list)
        return order_ids

    def write(self, vals):
        LoyaltyPoint = self.env['loyalty.point']
        prec = self.env['decimal.precision'].precision_get('Loyalty')
        if 'state' in vals:
            if vals['state'] == 'paid':
                for r in self:
                    if r.refund_original_order_id:
                        for line in r.lines:
                            if not float_is_zero(line.loyalty_points, precision_digits=prec):
                                data = line._prepare_loyalty_point_data()
                                LoyaltyPoint.create(data)
        return super(PosOrder, self).write(vals)

    def get_won_points(self):
        if not self.config_id.loyalty_id or not self.partner_id:
            return 0
        total_points = 0
        for line in self.lines:
            total_points += line.get_won_points()
        if not self.refund_original_order_id:
            total_points += float_round(self.config_id.loyalty_id.pp_order, precision_rounding=self.config_id.loyalty_id.rounding)
        else:
            total_points -= float_round(self.config_id.loyalty_id.pp_order, precision_rounding=self.config_id.loyalty_id.rounding)

        return total_points

    def get_spent_points(self):
        if not self.config_id.loyalty_id or not self.partner_id:
            return 0.0
        points = 0.0
        for line in self.lines:
            points += line.get_spent_points()

        return points

    def get_new_points(self):
        if not self.config_id.loyalty_id or not self.partner_id:
            return 0.0
        return float_round(self.get_won_points() - self.get_spent_points(), precision_rounding=self.config_id.loyalty_id.rounding)
