from odoo import api, models, fields

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


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
            res['delivery_date'] = self.env['to.base'].convert_time_to_utc(fields.Datetime.from_string(ui_order['delivery_date']))\
                                                      .strftime(DTF)
        return res

    def _create_order_picking(self):
        self.ensure_one()
        if self.to_delivery:
            self = self.with_context(
                force_delivery_date=self.delivery_date,
                force_carrier_id=self.carrier_id.id,
                ignore_action_done=True,
            )
        return super(PoSOrder, self)._create_order_picking()
