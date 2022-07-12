from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    fleet_vehicle_service_ids = fields.One2many('fleet.vehicle.log.services', 'invoice_id', string='Vehicle Services', groups='viin_fleet.group_fleet_vehicle_log_services_read', readonly=True)


    def action_post(self):
        res = super(AccountMove, self).action_post()
        self.mapped('fleet_vehicle_service_ids')._generate_anlytic_lines()
        return res

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        company_id = self.company_id.id
        p = self.partner_id if not company_id else self.partner_id.with_company(company_id)
        if p:

            if self.move_type in ('in_invoice', 'in_refund'):
                invoice_lines = self.invoice_line_ids or self.env['account.move.line']
                partners = p + p.commercial_partner_id + p.child_ids
                VehicleService = self.env['fleet.vehicle.log.services']
                vehicle_services = VehicleService.search([
                    ('vendor_id', 'in', partners.ids),
                    ('invoice_line_id', '=', False),
                    ('currency_id', '=', self.currency_id.id)])
                for vehicle_service in vehicle_services:
                    new_line_vals = vehicle_service._prepare_invoice_line_data(self.fiscal_position_id)
                    new_line_vals['move_id'] = self.id
                    new_line = invoice_lines.new(new_line_vals)
                    new_line._onchange_price_subtotal()
                    invoice_lines += new_line
                invoice_lines._onchange_mark_recompute_taxes()
                self.invoice_line_ids = invoice_lines
                self._onchange_currency()
        return res
    
    def write(self, vals):
        super(AccountMove, self).write(vals)
        if vals.get('invoice_date', False):
            vehicle_log_services = self.fleet_vehicle_service_ids.filtered(lambda l: l.created_from_invoice_line_id)
            if vehicle_log_services:
                vehicle_log_services.write({'date': vals.get('invoice_date', False)})
