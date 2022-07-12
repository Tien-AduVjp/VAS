from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class VehicleTripRegisterCostWizard(models.TransientModel):
    _inherit = 'vehicle.trip.register.cost.wizard'


    product_id = fields.Many2one('product.product', string='Invoiceable Product',
                                 help="The product that will be used when invoicing this cost")

    @api.constrains('service_type_id', 'product_id')
    def _check_constrains_service_type_id_product_id(self):
        for r in self:
            if r.service_type_id and r.product_id:
                if r.service_type_id.product_id:
                    if r.service_type_id.product_id.id != r.product_id.id:
                        raise ValidationError(_("There is a discrepancy between the product (%s) you selected and"
                                                " the product (%s) predefined for the service type %s")
                                              % (r.product_id.name, r.service_type_id.product_id.name, r.service_type_id.name))

    @api.onchange('trip_id')
    def _onchange_trip_id(self):
        if self.trip_id:
            vehicle_id = self.trip_id.vehicle_id
            if vehicle_id:
                if vehicle_id.company_id:
                    self.company_id = vehicle_id.company_id

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.currency_id = self.company_id.currency_id

    @api.onchange('service_type_id')
    def _onchange_service_type_id(self):
        if self.service_type_id:
            if self.service_type_id.product_id:
                self.product_id = self.service_type_id.product_id

    @api.model
    def _prepare_cost_data(self):
        res = super(VehicleTripRegisterCostWizard, self)._prepare_cost_data()

        product_id = self.product_id and self.product_id or False
        if not product_id:
            product_id = self.service_type_id and self.service_type_id.product_id

        res['product_id'] = product_id and product_id.id or False

        return res
