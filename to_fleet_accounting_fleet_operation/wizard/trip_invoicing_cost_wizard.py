from odoo import fields, models, api, _
from odoo.exceptions import UserError

class TripInvoicingCostWizard(models.TransientModel):
    _name = 'trip.invoicing.cost.wizard'
    _inherit = 'abstract.fleet.vehicle.log.services.invoicing.wizard'
    _description = "Invoicing Trip's Costs Wizard"

    @api.model
    def _get_trips(self):
        active_ids = self._context.get('active_ids', False)
        if active_ids:
            return self.env['fleet.vehicle.trip'].browse(active_ids).ids
        return []

    trip_ids = fields.Many2many('fleet.vehicle.trip', string='Trips to Invoice', default=_get_trips)

    vehicle_service_ids = fields.Many2many('fleet.vehicle.log.services',
                                        string='Services to Invoice',
                                        compute='_compute_vehicle_service_ids',
                                        readonly=False,
                                        store=True,
                                        domain="[('trip_id','in',trip_ids),('invoice_line_id','=',False),('vendor_id','!=',False)]",
                                        help="The services having a vendor but have not been invoiced will be loaded here upon you change the trip(s)")

    @api.depends('trip_ids')
    def _compute_vehicle_service_ids(self):
        vehicle_service_ids = []
        for trip in self.trip_ids:
            if trip.services_invoiced:
                continue
            if trip.log_services_ids:
                uninvoiced_services = trip.log_services_ids.filtered(lambda r: not r.invoice_line_id and r.vendor_id)
                if not uninvoiced_services:
                    continue
                vehicle_service_ids += uninvoiced_services.ids
        self.vehicle_service_ids = [(6, 0, vehicle_service_ids)]

    def create_invoices(self):
        self.ensure_one()
        for vehicle_service_id in self.vehicle_service_ids:
            if vehicle_service_id.id not in self.trip_ids.log_services_ids.ids:
                raise UserError(_("You cannot create invoice the vehicle service of another trip"))
        return self.create_invoice_from_services(self.vehicle_service_ids)
