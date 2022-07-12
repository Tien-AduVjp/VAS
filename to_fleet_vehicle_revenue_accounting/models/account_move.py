from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"
    
    fleet_vehicle_revenue_ids = fields.One2many('fleet.vehicle.revenue', 'invoice_id', string='Vehicle Revenues', readonly=True, groups="to_fleet_vehicle_revenue.fleet_vehicle_revenue_group_read")

    @api.model
    def invoice_line_move_line_get(self):
        # TODO: remove from 13.0
        InvoiceLine = self.env['account.move.line']
        ml_data = []

        res = super(AccountMove, self).invoice_line_move_line_get()
        for line_data in res:
            line = InvoiceLine.browse(line_data['invl_id'])
            if line.fleet_vehicle_revenue_ids:
                # split move line into multiple if more that one revenue
                if len(line.fleet_vehicle_revenue_ids) > 1:
                    for fleet_vehicle_revenue in line.fleet_vehicle_revenue_ids:
                        new_line = line_data.copy()
                        new_line['vehicle_revenue_id'] = fleet_vehicle_revenue.id
                        new_line['price'] = fleet_vehicle_revenue.amount
                        ml_data.append(new_line)
                else:
                    line_data['vehicle_revenue_id'] = line.fleet_vehicle_revenue_ids[0].id
                    ml_data.append(line_data)
            else:
                ml_data.append(line_data)
        return ml_data

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountMove, self).line_get_convert(line, part)
        if 'vehicle_revenue_id' in line:
            res['vehicle_revenue_id'] = line['vehicle_revenue_id']
        return res

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for r in self:
            for revenue in r.fleet_vehicle_revenue_ids:
                revenue.write({'date': revenue.invoice_id.invoice_date})
        return res

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        company_id = self.company_id.id
        p = self.partner_id if not company_id else self.partner_id.with_context(force_company=company_id)
        if p:

            if self.type in ('out_invoice', 'out_refund'):
                invoice_line_ids = self.invoice_line_ids or self.env['account.move.line']
                partner_ids = p + p.commercial_partner_id + p.child_ids
                VehicleRevenue = self.env['fleet.vehicle.revenue']
                vehicle_revenue_ids = VehicleRevenue.search([
                    ('customer_id', 'in', partner_ids.ids),
                    ('invoice_line_id', '=', False),
                    ('currency_id', '=', self.currency_id.id)])
                for vehicle_revenue_id in vehicle_revenue_ids:
                    new_line = invoice_line_ids.new(vehicle_revenue_id._prepare_invoice_line_data(self.fiscal_position_id))
                    invoice_line_ids += new_line
                self.invoice_line_ids = invoice_line_ids

        return res
