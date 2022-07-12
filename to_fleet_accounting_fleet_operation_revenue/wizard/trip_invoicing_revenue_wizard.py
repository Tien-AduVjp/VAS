from odoo import fields, models, api, _


class TripInvoicingRevenueWizard(models.TransientModel):
    _name = 'trip.invoicing.revenue.wizard'
    _inherit = 'abstract.fleet.vehicle.revenue.invoicing.wizard'
    _description = "Invoicing Trip's Revenues Wizard"

    @api.model
    def _get_trips(self):
        active_ids = self._context.get('active_ids', False)
        if active_ids:
            return self.env['fleet.vehicle.trip'].browse(active_ids).ids
        return []

    trip_ids = fields.Many2many('fleet.vehicle.trip', string='Trips to Invoice', default=_get_trips)
    vehicle_revenue_ids = fields.Many2many('fleet.vehicle.revenue', string='Revenues to Invoice',
                                        help="The revenues having a customer defined but have not been invoiced will be loaded here upon you change the trip(s)")

    @api.onchange('trip_ids')
    def _onchange_trip_ids(self):
        res = {}
        vehicle_revenue_ids = []
        for trip in self.trip_ids:
            if trip.revenues_invoiced:
                continue
            if trip.fleet_vehicle_revenue_ids:
                uninvoiced_revenues = trip.fleet_vehicle_revenue_ids.filtered(lambda r: not r.invoice_line_id and r.customer_id)
                if not uninvoiced_revenues:
                    continue
                vehicle_revenue_ids += uninvoiced_revenues.ids
        self.vehicle_revenue_ids = [(6, 0, vehicle_revenue_ids)]
        if self.trip_ids:
            res['domain'] = {'vehicle_revenue_ids': [('id', 'in', self.trip_ids.mapped('fleet_vehicle_revenue_ids').filtered(lambda r: not r.invoice_line_id and r.customer_id).ids)]}
        return res

#     @api.model
#     def _get_invoice_line_name(self, fleet_vehicle_revenue):
#         invl_name = super(TripInvoicingRevenueWizard, self)._get_invoice_line_name(fleet_vehicle_revenue)
#
#         if fleet_vehicle_revenue.trip_id:
#             invl_name = _("Trip #: %s\n%s") % (fleet_vehicle_revenue.trip_id.display_name, invl_name)
#
#         return invl_name

    def create_invoices(self):
        return self.create_invoice_from_revenues(self.vehicle_revenue_ids)

