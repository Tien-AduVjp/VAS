from odoo import models, fields, api


class VehicleRevenueAllocationLine(models.TransientModel):
    _name = 'vehicle.revenue.allocation.line'
    _description = 'Vehicle Revenue Allocation Line'

    vehicle_revenue_allocation_wizard_id = fields.Many2one('vehicle.revenue.allocation.wizard', string='Vehicle Revenue Allocation Wizard',
                                                           required=True, ondelete='cascade')
    invoice_line_id = fields.Many2one('account.move.line', string='Invoice Line', required=True, ondelete='cascade')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', related='invoice_line_id.currency_id', readonly=True, ondelete='cascade')
    revenue_subtype_id = fields.Many2one('fleet.service.type', string='Type', ondelete='cascade')
    amount = fields.Monetary(string='Amount')

    @api.onchange('invoice_line_id')
    def _onchange_invoice_line_id(self):
        res = {}
        FleetServiceType = self.env['fleet.service.type']
        if self.invoice_line_id:
            if self.invoice_line_id.product_id:
                domain = [('product_id', '=', self.invoice_line_id.product_id.id)]
                self.revenue_subtype_id = FleetServiceType.search(domain, limit=1)
                res['domain'] = {'revenue_subtype_id':domain + [('product_id', '=', False)]}
        return res

    @api.model
    def _prepare_vehicle_revenue_data(self):
        return {
            'vehicle_id': self.vehicle_id.id,
            'revenue_subtype_id': self.revenue_subtype_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'date': self.invoice_line_id.move_id.invoice_date,
            'company_id': self.invoice_line_id.company_id.id,
            'product_id': self.invoice_line_id.product_id.id,
            'invoice_line_id': self.invoice_line_id.id,
            'customer_id': self.invoice_line_id.partner_id.id,
            'created_from_invoice_line_id': self.invoice_line_id.id,
            }
