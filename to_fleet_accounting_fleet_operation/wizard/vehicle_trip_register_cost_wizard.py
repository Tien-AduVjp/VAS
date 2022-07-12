from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class VehicleTripRegisterCostWizard(models.TransientModel):
    _inherit = 'vehicle.trip.register.cost.wizard'

    @api.model
    def _get_default_company(self):
        return self.env.company

    @api.model
    def _get_default_currency(self):
        return self.env.company.currency_id

    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    product_id = fields.Many2one('product.product', string='Invoiceable Product',
                                 help="The product that will be used when invoicing this cost")
    company_id = fields.Many2one('res.company', string='Company', default=_get_default_company, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=_get_default_currency, required=True)

    amount = fields.Monetary(string='Amount', required=True)

    @api.constrains('cost_subtype_id', 'product_id')
    def _check_constrains_cost_subtype_id_product_id(self):
        for r in self:
            if r.cost_subtype_id and r.product_id:
                if r.cost_subtype_id.product_id:
                    if r.cost_subtype_id.product_id.id != r.product_id.id:
                        raise ValidationError(_("There is a discrepancy between the product (%s) you selected and"
                                                " the product (%s) predefined for the service type %s")
                                              % (r.product_id.name, r.cost_subtype_id.product_id.name, r.cost_subtype_id.name))

    @api.onchange('trip_id')
    def _onchange_trip_id(self):
        res = super(VehicleTripRegisterCostWizard, self)._onchange_trip_id()
        if self.trip_id:
            vehicle_id = self.trip_id.vehicle_id
            if vehicle_id:
                if vehicle_id.company_id:
                    self.company_id = vehicle_id.company_id
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.currency_id = self.company_id.currency_id

    @api.onchange('cost_subtype_id')
    def _onchange_cost_subtype_id(self):
        res = {}
        if self.cost_subtype_id:
            if self.cost_subtype_id.product_id:
                self.product_id = self.cost_subtype_id.product_id
                res['domain'] = {'product_id':[('id', '=', self.cost_subtype_id.product_id.id)]}
            else:
                res['domain'] = {'product_id':[('id', '>', 0)]}
        return res

    @api.model
    def _prepare_cost_data(self):
        res = super(VehicleTripRegisterCostWizard, self)._prepare_cost_data()

        product_id = self.product_id and self.product_id or False
        if not product_id:
            product_id = self.cost_subtype_id and self.cost_subtype_id.product_id

        res['vendor_id'] = self.vendor_id.id
        res['product_id'] = product_id and product_id.id or False
        res['company_id'] = self.company_id.id
        res['currency_id'] = self.currency_id.id
        return res
