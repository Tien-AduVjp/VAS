from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
import pytz


class PoSOrder(models.Model):
    _inherit = 'pos.order'

    carrier_id = fields.Many2one('delivery.carrier', string='Carrier')
    to_delivery = fields.Boolean(string='To Delivery')
    delivery_date = fields.Datetime(string='Delivery Date', help="The scheduled delivery Date")

    @api.model
    def _order_fields(self, ui_order):
        res = super(PoSOrder, self)._order_fields(ui_order)
        res['carrier_id'] = ui_order.get('carrier_id', False)
        res['to_delivery'] = ui_order.get('to_delivery', False)
        if ui_order.get('delivery_date', False):
            res['delivery_date'] = self.convert_time_to_utc(ui_order['delivery_date'])
        return res

    @api.model
    def create_from_ui(self, orders, draft=False):
        """ create a Pos order from the point of sale ui.
         """
        order_ids = super(PoSOrder, self).create_from_ui(orders)
        orders = self.browse( [order['id'] for order in order_ids] )
        for order in orders:
            if order.to_delivery:
                if order.picking_id:
                    order.picking_id.write({'carrier_id': order.carrier_id.id, 'scheduled_date': order.delivery_date})
        return order_ids

    def _force_picking_done(self, picking):
        """Force picking in order to be set as done."""
        self.ensure_one()

        # if no delivery, fallback to the super
        if not self.to_delivery:
            super(PoSOrder, self)._force_picking_done(picking)
        else:
            contains_tracked_products = any([(product_id.tracking != 'none') for product_id in self.lines.mapped('product_id')])

            # do not reserve for tracked products, the user will have manually specified the serial/lot numbers
            if contains_tracked_products:
                picking.action_confirm()
            else:
                picking.action_assign()

    def convert_time_to_utc(self, datetime_str):
        tz_name = self.env.user.tz
        if not tz_name:
            raise ValidationError(_("The user '%s' has no timezone specified. Please set it.") % (self.env.user.name,))
        local = pytz.timezone(tz_name)
        naive = fields.Datetime.from_string(datetime_str)
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return fields.Datetime.to_string(utc_dt)

