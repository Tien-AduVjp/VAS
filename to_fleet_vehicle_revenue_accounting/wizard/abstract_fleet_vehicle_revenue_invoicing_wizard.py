from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError


class AbstractFleetVehicleRevenueInvoicingWizard(models.TransientModel):
    _name = 'abstract.fleet.vehicle.revenue.invoicing.wizard'
    _description = 'Share business Logics between Fleet Vehicle Revenue Invoicing Wizards'

    def _prepare_invoice_data(self, customer, currency, company_id, revenues, journal_id):
        fiscal_position = customer.property_account_position_id or False
        inv_lines_vals_list = revenues._prepare_invoice_lines_data(fiscal_position)
        return {
            'type': 'out_invoice',
            'ref': False,
            'partner_id': customer.id,
            'invoice_line_ids': [(0, 0, vals) for vals in inv_lines_vals_list],
            'currency_id': currency.id,
            'fiscal_position_id': fiscal_position and fiscal_position.id or False,
            'company_id': company_id.id,
            'journal_id': journal_id.id,
            }

    @api.model
    def _create_invoice(self, customer, currency, company_id, revenues):
        fiscal_position_id = customer.property_account_position_id
        if isinstance(revenues, list):
            revenues = self.env['fleet.vehicle.revenue'].browse([revenue.id for revenue in revenues])
        invoice_line_ids = []
        for revenue in revenues:
            invoice_line_ids.append((0, 0, revenue._prepare_invoice_line_data(fiscal_position_id)))

        # find a journal
        journal_domain = [
                ('type', '=', 'sale'),
                ('company_id', '=', company_id.id),
            ]
        if currency.id != company_id.currency_id.id:
            journal_domain.append(('currency_id', '=', currency.id))
        else:
            journal_domain.append(('currency_id', '=', False))
        journal_id = self.env['account.journal'].search(journal_domain, limit=1)
        if not journal_id:
            raise ValidationError(_("No Sales Journal found for the currency %s") % (currency.name,))

        Invoice = self.env['account.move']
        invoice = Invoice.search([
            ('partner_id', '=', customer.id),
            ('state', '=', 'draft'),
            ('type', '=', 'out_invoice'),
            ('currency_id', '=', currency.id),
            ('company_id', '=', company_id.id),
            ('journal_id', '=', journal_id.id)], limit=1)

        if invoice:
            inv_lines_vals_list = revenues._prepare_invoice_lines_data(customer.property_account_position_id or False)
            invoice.write({'invoice_line_ids': [(0, 0, vals) for vals in inv_lines_vals_list]})
        else:
            invoice_vals = self._prepare_invoice_data(customer, currency, company_id, revenues, journal_id)
            invoice = Invoice.create(invoice_vals)
        invoice._onchange_partner_id()
        return invoice

    def create_invoice_from_revenues(self, fleet_vehicle_revenue_ids):
        invoiceable_lines = fleet_vehicle_revenue_ids.filtered(lambda r: not r.invoice_line_id)
        if not invoiceable_lines:
            raise UserError(_("No invoiceable revenues for invoicing! Please select at least one that has not been invoiced."))

        data = {}

        for revenue in invoiceable_lines:
            if revenue.company_id not in data.keys():
                data[revenue.company_id] = {}

            if not revenue.currency_id:
                raise ValidationError(_("The revenue id: %d has no currency set. Hence, cannot create invoice for it.")
                                      % (revenue.id,))
            if revenue.currency_id not in data[revenue.company_id].keys():
                data[revenue.company_id][revenue.currency_id] = {}

            if not revenue.customer_id:
                raise ValidationError(_("The revenue id: %d has no customer set. Hence, cannot create invoice for it.")
                                      % (revenue.id,))

            if revenue.customer_id not in data[revenue.company_id][revenue.currency_id].keys():
                data[revenue.company_id][revenue.currency_id][revenue.customer_id] = []

            data[revenue.company_id][revenue.currency_id][revenue.customer_id].append(revenue)

        for company_id in data.keys():
            for currency in data[company_id]:
                for customer in data[company_id][currency]:
                    self._create_invoice(customer, currency, company_id, data[company_id][currency][customer])

        if self._context.get('open_invoices', False):
            return invoiceable_lines.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
