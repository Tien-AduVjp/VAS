from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    vehicle_revenue_id = fields.Many2one('fleet.vehicle.revenue', string='Vehicle Revenue', ondelete='restrict',
                                      help="This field is to indicate that the move line relates to a"
                                      " vehicle revenue registered in the Fleet Management application")
    fleet_vehicle_revenue_ids = fields.One2many('fleet.vehicle.revenue', 'invoice_line_id', string='Vehicle revenues')
    fleet_vehicle_revenues_count = fields.Integer(string='Vehicle revenue Count', compute='_compute_fleet_vehicle_revenues_count', store=True)

    has_vehicle_revenue = fields.Boolean(string='Has Vehicle revenue', compute='_compute_has_vehicle_revenue', store=True, 
                                         help="This technical field to indicate if this invoice line refers vehicle revenue(s).")

    @api.constrains('fleet_vehicle_cost_ids', 'fleet_vehicle_revenue_ids')
    def _check_constrains_vehicle_revenue_revenue(self):
        for r in self:
            if r.fleet_vehicle_cost_ids and r.fleet_vehicle_revenue_ids:
                raise ValidationError(_("A Journal Item cannot refer to both vehicle cost and vehicle revenue. It is able to refer to either or neither of those"))

    @api.constrains('currency_id', 'price_subtotal', 'fleet_vehicle_revenue_ids')
    def _check_invl_vehicle_revenue_constrains(self):
        precision = self.env['decimal.precision'].precision_get('Product Price')
        for r in self.filtered(lambda r: r.fleet_vehicle_revenue_ids):
            total = 0.0
            for revenue in r.fleet_vehicle_revenue_ids:
                if revenue.currency_id.id != r.move_id.currency_id.id:
                    raise ValidationError(_("Vehicle revenue (id: %d)'s currency (%s) must be the same as the invoice's one (%s)")
                                          % (revenue.id, revenue.currency_id.name, r.currency_id.name))
                total += revenue.amount

            if float_compare(r.price_subtotal, total, precision_digits=precision) != 0:
                raise ValidationError(_('The sum of the vehicle revenue (%d) of the invoice line'
                                        ' is not equal to the Amount of the invoice line (%d).'
                                        ' Please adjust the unit price to make the Amount equal.')
                                      % (total, r.price_subtotal))
    
    @api.depends('fleet_vehicle_revenue_ids')
    def _compute_fleet_vehicle_revenues_count(self):
        revenues = self.env['fleet.vehicle.revenue'].read_group([('invoice_line_id', 'in', self.ids)], ['invoice_line_id'], ['invoice_line_id'])
        mapped_data = dict([(d['invoice_line_id'][0], d['invoice_line_id_count']) for d in revenues])
        for r in self:
            r.fleet_vehicle_revenues_count = mapped_data.get(r.id, 0)
    
    @api.depends('fleet_vehicle_revenue_ids')
    def _compute_has_vehicle_revenue(self):
        for r in self:
            r.has_vehicle_revenue = r.fleet_vehicle_revenue_ids and True or False
    
    @api.model
    def _prepare_vehicle_revenue_allocation_line_data(self, vehicle_id, vehicle_count):
        FleetServiceType = self.env['fleet.service.type']
        return {
            'invoice_line_id': self._origin and self._origin.id or self.id,
            'vehicle_id': vehicle_id._origin and vehicle_id._origin.id or vehicle_id.id,
            'revenue_subtype_id': self.product_id and FleetServiceType.search([('product_id', '=', self.product_id.id)], limit=1) or False,
            'amount': self.price_subtotal / vehicle_count,
            }
    
    def unlink(self):
        for r in self:
            r.fleet_vehicle_revenue_ids.filtered(lambda c: c.created_from_invoice_line_id).unlink()
        return super(AccountMoveLine, self).unlink()
    
    def action_vehicle_revenue_allocation_wizard(self):
        if not self:
            raise UserError(_("Please hit Save button first!"))

        action = self.env.ref('to_fleet_vehicle_revenue_accounting.action_vehicle_revenue_allocation_wizard')
        result = action.read()[0]
        return result
