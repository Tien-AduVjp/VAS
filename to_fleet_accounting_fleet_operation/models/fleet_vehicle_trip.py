import ast

from odoo import fields, models, api


class FleetVehicleTrip(models.Model):
    _inherit = 'fleet.vehicle.trip'

    costs_invoiced = fields.Boolean(string='Costs Invoiced', compute='_compute_costs_invoiced', store=True,
                                    help="This technical field is to indicate if all the trip's costs have been fully invoiced."
                                    " Note: this field takes True value when no cost is registered for the trip")

    vendor_invoice_ids = fields.Many2many('account.move', 
                                          'account_invoice_fleet_vehicle_trip_vendor_rel', 
                                          'fleet_vehicle_trip_id','account_invoice_id',
                                          string='Vendor Bills', compute='_compute_vendor_invoice_ids', store=True)
    vendor_invoices_count = fields.Integer(string='Vendor Bills Count', compute='_compute_vendor_invoices_count', store=True)

    @api.depends('fleet_vehicle_cost_ids', 'fleet_vehicle_cost_ids.invoice_line_id', 'fleet_vehicle_cost_ids.created_from_invoice_line_id')
    def _compute_costs_invoiced(self):
        for r in self:
            uninvoiced_costs = r.fleet_vehicle_cost_ids.filtered(lambda cost: not cost.invoice_line_id and not cost.created_from_invoice_line_id)
            if uninvoiced_costs:
                r.costs_invoiced = False
            else:
                r.costs_invoiced = True

    @api.depends('fleet_vehicle_cost_ids', 'fleet_vehicle_cost_ids.invoice_line_id', 'fleet_vehicle_cost_ids.invoice_line_id.move_id')
    def _compute_vendor_invoice_ids(self):
        for r in self:
            invoiced_costs = r.fleet_vehicle_cost_ids.filtered(lambda cost: cost.invoice_line_id)
            if invoiced_costs:
                r.vendor_invoice_ids = invoiced_costs.invoice_id.ids
            else:
                r.vendor_invoice_ids = False

    @api.depends('vendor_invoice_ids')
    def _compute_vendor_invoices_count(self):
        for r in self:
            r.vendor_invoices_count = len(r.vendor_invoice_ids)

    def action_view_vendor_invoices(self):
        '''
        This function returns an action that display existing vendor bills of given trip ids.
        When only one found, show the vendor bill immediately.
        '''
        self.ensure_one()
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]

        # Choose a default account journal in the same currency in case a new invoice is created    
        default_journal_id = self.env['account.journal'].search([('type', '=', 'purchase'),
                                                                 ('company_id', '=', self.vehicle_id.company_id.id or self.env.company.id),
                                                                 ('currency_id', '=', self.env.company.currency_id.id),
                                                                 ], limit=1)
        ctx = action.get('context', {})
        if type(ctx) == str:
            ctx = ast.literal_eval(ctx)
        
        if default_journal_id:
            ctx['default_journal_id'] = default_journal_id.id
        action['context'] = ctx
        
        if len(self.vendor_invoice_ids):
            action['domain'] = [('id', 'in', self.vendor_invoice_ids.ids)]
        else:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = self.vendor_invoice_ids.id
        return action
