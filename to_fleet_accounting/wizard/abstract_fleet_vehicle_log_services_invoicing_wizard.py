from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError


class AbstractFleetVehicleLogServicesInvoicingWizard(models.AbstractModel):
    _name = 'abstract.fleet.vehicle.log.services.invoicing.wizard'
    _description = 'Share business Logics between Fleet Vehicle Service Invoicing Wizards'

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

    def _prepare_invoice_data(self, vendor, currency, company_id, services, journal):
        fiscal_position = vendor.property_account_position_id or False
        inv_lines_vals_list = services._prepare_invoice_lines_data(fiscal_position)
        return {
            'move_type': 'in_invoice',
            'ref': False,
            'partner_id': vendor.id,
            'invoice_line_ids': [(0, 0, vals) for vals in inv_lines_vals_list],
            'currency_id': currency.id,
            'fiscal_position_id': fiscal_position and fiscal_position.id or False,
            'company_id': company_id.id,
            'journal_id': journal.id,
            }

    @api.model
    def _create_invoice(self, vendor, currency, company, services):
        if isinstance(services, list):
            services = self.env['fleet.vehicle.log.services'].browse([service.id for service in services])
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
            ('move_type', '=', 'in_invoice'),
            ('currency_id', '=', currency.id),
            ('company_id', '=', company.id),
            ('journal_id', '=', journal.id)], limit=1)

        if invoice:
            inv_lines_vals_list = services._prepare_invoice_lines_data(vendor.property_account_position_id or False)
            invoice.write({'invoice_line_ids': [(0, 0, vals) for vals in inv_lines_vals_list]})
        else:
            invoice_vals = self._prepare_invoice_data(vendor, currency, company, services, journal)
            invoice = Invoice.create(invoice_vals)
        invoice._onchange_partner_id()
        return invoice

    def create_invoice_from_services(self, fleet_vehicle_log_services_ids):
        invoiceable_lines = fleet_vehicle_log_services_ids.filtered(lambda r: r.invoiceable)
        if not invoiceable_lines:
            raise UserError(_("No invoiceable services for invoicing! Please select at least one that has not been invoiced."
                              " Please note that a vehicle service is considered as 'Invoiceable' when it has a vendor specified"
                              " AND has not been invoiced yet."))

        data = {}

        for service in invoiceable_lines:
            if service.company_id not in data.keys():
                data[service.company_id] = {}

            if not service.currency_id:
                raise ValidationError(_("The service id: %d has no currency set. Hence, cannot create invoice for it.")
                                      % (service.id,))
            if service.currency_id not in data[service.company_id].keys():
                data[service.company_id][service.currency_id] = {}

            if not service.vendor_id:
                raise ValidationError(_("The service id: %d has no vendor set. Hence, cannot create invoice for it.")
                                      % (service.id,))

            if service.vendor_id not in data[service.company_id][service.currency_id].keys():
                data[service.company_id][service.currency_id][service.vendor_id] = []

            data[service.company_id][service.currency_id][service.vendor_id].append(service)

        for company_id in data.keys():
            for currency in data[company_id]:
                for vendor in data[company_id][currency]:
                    self._create_invoice(vendor, currency, company_id, data[company_id][currency][vendor])

        invoiceable_lines.invalidate_cache(ids=invoiceable_lines.ids)
        if self._context.get('open_invoices', False):
            return invoiceable_lines.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
