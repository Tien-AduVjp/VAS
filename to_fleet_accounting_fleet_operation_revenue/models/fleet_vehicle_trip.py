from odoo import fields, models, api


class FleetVehicleTrip(models.Model):
    _inherit = 'fleet.vehicle.trip'

    fleet_vehicle_revenue_ids = fields.One2many('fleet.vehicle.revenue', 'trip_id', string='Vehicle Revenues')
    fleet_vehicle_revenues_count = fields.Integer(string='Vehicle Revenues Count', compute='_compute_fleet_vehicle_revenues_count', store=True)

    revenues_invoiced = fields.Boolean(string='Revenues Invoiced', compute='_compute_revenues_invoiced', store=True,
                                    help="This technical field is to indicate if all the trip's revenues have been fully invoiced."
                                    " Note: this field takes True value when no revenue is registered for the trip")

    customer_invoice_ids = fields.Many2many('account.move','account_invoice_fleet_vehicle_trip_customer_rel','fleet_vehicle_trip_id','account_invoice_id',
                                            string='Customer Invoices', compute='_compute_customer_invoice_ids', store=True)
    customer_invoices_count = fields.Integer(string='Customer Invoices Count', compute='_compute_customer_invoices_count', store=True)

    @api.depends('fleet_vehicle_revenue_ids')
    def _compute_fleet_vehicle_revenues_count(self):
        for r in self:
            r.fleet_vehicle_revenues_count = len(r.fleet_vehicle_revenue_ids)

    @api.depends('fleet_vehicle_revenue_ids', 'fleet_vehicle_revenue_ids.invoice_line_id', 'fleet_vehicle_revenue_ids.created_from_invoice_line_id')
    def _compute_revenues_invoiced(self):
        for r in self:
            uninvoiced_revenues = r.fleet_vehicle_revenue_ids.filtered(lambda revenue: not revenue.invoice_line_id and not revenue.created_from_invoice_line_id)
            if uninvoiced_revenues:
                r.revenues_invoiced = False
            else:
                r.revenues_invoiced = True

    @api.depends('fleet_vehicle_revenue_ids', 'fleet_vehicle_revenue_ids.invoice_line_id', 'fleet_vehicle_revenue_ids.invoice_line_id.move_id')
    def _compute_customer_invoice_ids(self):
        for r in self:
            invoiced_revenues = r.fleet_vehicle_revenue_ids.filtered(lambda revenue: revenue.invoice_line_id)
            if invoiced_revenues:
                r.customer_invoice_ids = invoiced_revenues.mapped('invoice_id').ids
            else:
                r.customer_invoice_ids = False

    @api.depends('customer_invoice_ids')
    def _compute_customer_invoices_count(self):
        for r in self:
            r.customer_invoices_count = len(r.customer_invoice_ids)

    def action_view_customer_invoices(self):
        '''
        This function returns an action that display existing customer invoices of given trip ids.
        When only one found, show the customer invoice immediately.
        '''
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]

        # override the context to get rid of the default filtering
        result['context'] = {'type': 'out_invoice'}

        if not self.customer_invoice_ids:
            company = self.env.company
            # if the trip's vehicle has company, select it
            if self.vehicle_id.company_id:
                    company = self.vehicle_id.company_id

            # Choose a default account journal in the same currency in case a new invoice is created
            journal_domain = [
                ('type', '=', 'sale'),
                ('company_id', '=', company.id),
                ('currency_id', '=', self.env.company.currency_id.id),
            ]
            default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
            if default_journal_id:
                result['context']['default_journal_id'] = default_journal_id.id
        else:
            # Use the same account journal than a previous invoice
            result['context']['default_journal_id'] = self.customer_invoice_ids[0].journal_id.id

        # choose the view_mode accordingly
        if len(self.customer_invoice_ids) != 1:
            result['domain'] = [('id', 'in', self.customer_invoice_ids.ids)]
        elif len(self.customer_invoice_ids) == 1:
            res = self.env.ref('account.view_move_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.customer_invoice_ids.id
        return result
