from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    fleet_vehicle_cost_ids = fields.One2many('fleet.vehicle.cost', 'invoice_id', string='Vehicle Costs', groups='to_fleet_accounting.fleet_vehicle_cost_group_read', readonly=True)

    @api.model
    def invoice_line_move_line_get(self):
        InvoiceLine = self.env['account.move.line']
        ml_data = []

        res = super(AccountMove, self).invoice_line_move_line_get()
        for line_data in res:
            line = InvoiceLine.browse(line_data['invl_id'])
            if line.fleet_vehicle_cost_ids:
                # split move line into multiple if more that one cost
                if len(line.fleet_vehicle_cost_ids) > 1:
                    for fleet_vehicle_cost in line.fleet_vehicle_cost_ids:
                        new_line = line_data.copy()
                        new_line['vehicle_cost_id'] = fleet_vehicle_cost.id
                        new_line['price'] = fleet_vehicle_cost.amount
                        ml_data.append(new_line)
                else:
                    line_data['vehicle_cost_id'] = line.fleet_vehicle_cost_ids[0].id
                    ml_data.append(line_data)
            else:
                ml_data.append(line_data)
        return ml_data

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountMove, self).line_get_convert(line, part)
        if 'vehicle_cost_id' in line:
            res['vehicle_cost_id'] = line['vehicle_cost_id']
        return res

    def action_post(self):
        res = super(AccountMove, self).action_post()
        self.mapped('fleet_vehicle_cost_ids')._generate_anlytic_lines()
        return res

#     def action_invoice_cancel(self):
#         res = super(AccountMove, self).action_invoice_cancel()
#         if not self.env.context.get('keep_vehicle_cost', False):
#             for r in self:
#                 if r.fleet_vehicle_cost_ids:
#                     r.fleet_vehicle_cost_ids.unlink()
#         return res
# 
#     def _action_reopen(self):
#         self.action_invoice_cancel()
#         self.action_invoice_draft()
#         self.action_invoice_open()
#         return True

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        company_id = self.company_id.id
        p = self.partner_id if not company_id else self.partner_id.with_context(force_company=company_id)
        if p:

            if self.type in ('in_invoice', 'in_refund'):
                invoice_line_ids = self.invoice_line_ids or self.env['account.move.line']
                partner_ids = p + p.commercial_partner_id + p.child_ids
                VehicleCost = self.env['fleet.vehicle.cost']
                vehicle_cost_ids = VehicleCost.search([
                    ('vendor_id', 'in', partner_ids.ids),
                    ('invoice_line_id', '=', False),
                    ('currency_id', '=', self.currency_id.id)])
                for vehicle_cost_id in vehicle_cost_ids:
                    new_line = invoice_line_ids.new(vehicle_cost_id._prepare_invoice_line_data(self.fiscal_position_id))
                    invoice_line_ids += new_line
                self.invoice_line_ids = invoice_line_ids

        return res
