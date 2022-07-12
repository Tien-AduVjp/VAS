from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError


class AbstractFleetVehicleCostInvoicingWizard(models.AbstractModel):
    _name = 'abstract.fleet.vehicle.cost.invoicing.wizard'
    _description = 'Share business Logics between Fleet Vehicle Cost Invoicing Wizards'

    def _find_journal_domain(self, currency, company):
        # find a journal
        journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', company.id),
            ]
        if currency.id != company.currency_id.id:
            journal_domain.append(('currency_id', '=', currency.id))
        else:
            journal_domain.append(('currency_id', '=', False))
        return journal_domain

    def _find_journal(self, currency, company):
        return self.env['account.journal'].search(self._find_journal_domain(currency, company), limit=1)

    def _prepare_invoice_data(self, vendor, currency, company_id, costs, journal):
        fiscal_position = vendor.property_account_position_id or False
        inv_lines_vals_list = costs._prepare_invoice_lines_data(fiscal_position)
        return {
            'type': 'in_invoice',
            'ref': False,
            'partner_id': vendor.id,
            'invoice_line_ids': [(0, 0, vals) for vals in inv_lines_vals_list],
            'currency_id': currency.id,
            'fiscal_position_id': fiscal_position and fiscal_position.id or False,
            'company_id': company_id.id,
            'journal_id': journal.id,
            }

    @api.model
    def _create_invoice(self, vendor, currency, company, costs):
        if isinstance(costs, list):
            costs = self.env['fleet.vehicle.cost'].browse([cost.id for cost in costs])
        if self.env.company != company:
            raise ValidationError(_("You were trying to generate invoices for the company %s while you are on the %s."
                                    " Please switch to the company %s then retry.")
                                    % (company.name, self.env.company.name, company.name))

        journal = self._find_journal(currency, company)
        if not journal:
            raise ValidationError(_("No Purchase Journal found for the currency %s") % (currency.name,))

        Invoice = self.env['account.move']

        invoice = Invoice.search([
            ('partner_id', '=', vendor.id),
            ('state', '=', 'draft'),
            ('type', '=', 'in_invoice'),
            ('currency_id', '=', currency.id),
            ('company_id', '=', company.id),
            ('journal_id', '=', journal.id)], limit=1)

        if invoice:
            inv_lines_vals_list = costs._prepare_invoice_lines_data(vendor.property_account_position_id or False)
            invoice.write({'invoice_line_ids': [(0, 0, vals) for vals in inv_lines_vals_list]})
        else:
            invoice_vals = self._prepare_invoice_data(vendor, currency, company, costs, journal)
            invoice = Invoice.create(invoice_vals)
        invoice._onchange_partner_id()
        return invoice

    def create_invoice_from_costs(self, fleet_vehicle_cost_ids):
        invoiceable_lines = fleet_vehicle_cost_ids.filtered(lambda r: r.invoiceable)
        if not invoiceable_lines:
            raise UserError(_("No invoiceable costs for invoicing! Please select at least one that has not been invoiced."
                              " Please note that a vehicle cost is considered as 'Invoiceable' when it has a vendor specified"
                              " AND has not been invoiced yet."))

        data = {}

        for cost in invoiceable_lines:
            if cost.company_id not in data.keys():
                data[cost.company_id] = {}

            if not cost.currency_id:
                raise ValidationError(_("The cost id: %d has no currency set. Hence, cannot create invoice for it.")
                                      % (cost.id,))
            if cost.currency_id not in data[cost.company_id].keys():
                data[cost.company_id][cost.currency_id] = {}

            if not cost.vendor_id:
                raise ValidationError(_("The cost id: %d has no vendor set. Hence, cannot create invoice for it.")
                                      % (cost.id,))

            if cost.vendor_id not in data[cost.company_id][cost.currency_id].keys():
                data[cost.company_id][cost.currency_id][cost.vendor_id] = []

            data[cost.company_id][cost.currency_id][cost.vendor_id].append(cost)

        for company_id in data.keys():
            for currency in data[company_id]:
                for vendor in data[company_id][currency]:
                    self._create_invoice(vendor, currency, company_id, data[company_id][currency][vendor])

        if self._context.get('open_invoices', False):
            return invoiceable_lines.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

