from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class FleetVehicleLogServices(models.Model):
    _name = 'fleet.vehicle.log.services'
    _inherit = ['fleet.vehicle.log.services','abstract.vehicle.service.revenue']


    product_id = fields.Many2one(compute='_compute_product_id', readonly=False, store=True)
    created_from_invoice_line_id = fields.Many2one(help="A technical field to indicate that this service was created from an invoice line", copy=False)
    invoiceable = fields.Boolean(string='Invoiceable', compute='_compute_invoiceable', store=True, default=False, copy=False)
    currency_id = fields.Many2one(store=True)

    def _get_invoice_line_name(self):
        self.ensure_one()
        if self.product_id and self.product_id.description_purchase:
            product_desc = self.product_id.description_purchase
        else:
            product_desc = ''
        return "%s\n%s" % (self.display_name, product_desc)

    def _get_account_id(self):
        self.ensure_one()
        ir_property_obj = self.env['ir.property']
        account_id = False

        # if service has product specified, get account from product settings
        if self.product_id:
            account_id = self.product_id.product_tmpl_id._get_product_accounts()['expense']

        # otherwise. get the company property
        if not account_id:
            account_id = ir_property_obj._get('property_account_expense_categ_id', 'product.category')

        if not account_id:
            if self.product_id:
                raise UserError(
                    _('There is no expense account defined for this product: "%s". You may have to install a chart of account from Accounting app, Settings menu.')
                    % (self.product_id.name,))
            else:
                raise UserError(
                    _("There is neither product defined for the service id: %d nor expense account in product category property.")
                    % (self.id,))

        return account_id

    def _prepare_analytic_line_data(self):
        self.ensure_one()
        analytic_account = self._get_analytic_account()
        if not analytic_account:
            raise ValidationError(_("There is no analytic account specified for the vehicle %s") % self.vehicle_id.display_name)
        product = self.get_product()
        return {
            'name': self.vehicle_id.name,
            'account_id': analytic_account.id,
            'tag_ids': [(6, 0, self._get_analytic_tags().ids)],
            'date': self.date or self.invoice_id.date,
            'company_id': self.company_id.id,
            'unit_amount': self.quantity,
            'amount':-1 * self.amount,
            'partner_id': self.vendor_id and self.vendor_id.id or False,
            'vehicle_service_id': self.id,
            'move_id': self.invoice_line_id and self.invoice_line_id.id or False,
            'product_id': product and product.id or False
            }

    def _prepare_analytic_lines_data(self):
        vals_list = []
        for r in self:
            vals_list.append(r._prepare_analytic_line_data())
        return vals_list

    def _generate_anlytic_lines(self):
        return self.env['account.analytic.line'].create(self._prepare_analytic_lines_data())

    def _get_tax_ids(self, fiscal_position_id=None):
        self.ensure_one()
        taxes = False
        if self.product_id:
            taxes = self.product_id.supplier_taxes_id.filtered(lambda r: not self.company_id or r.company_id == self.company_id)
        if fiscal_position_id and taxes:
            taxes = fiscal_position_id.map_tax(taxes)
        return taxes

    def _prepare_invoice_line_data(self, fiscal_position_id=None):
        data = super(FleetVehicleLogServices, self)._prepare_invoice_line_data(fiscal_position_id)
        data.update({
            'price_unit': self.price_unit,
            'quantity': self.quantity,
            'fleet_vehicle_service_ids': [(6, 0, [self.id])],
            })
        return data

    def _is_invoiceable(self):
        if not self.invoice_line_id and self.vendor_id and not self.created_from_invoice_line_id:
            return True
        return False

    @api.depends('invoice_id', 'invoice_line_id', 'vendor_id', 'created_from_invoice_line_id')
    def _compute_invoiceable(self):
        for r in self:
            r.invoiceable = r._is_invoiceable()

    @api.constrains('product_id', 'service_type_id')
    def _check_constrains_product(self):
        for r in self:
            if r.service_type_id:
                if r.service_type_id.product_id and r.product_id:
                    if r.service_type_id.product_id.id != r.product_id.id:
                        raise ValidationError(_("The service must have the same product as its Type's product."
                                                " Otherwise, you must leave its Product field empty so that the"
                                                " Type's Product will be used."))

    @api.depends('service_type_id')
    def _compute_product_id(self):
        for r in self:
            r.product_id = r.service_type_id and r.service_type_id.product_id or False

    def get_product(self):
        return self.invoice_line_id.product_id or self.product_id or self.service_type_id.product_id or False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'service_type_id' in vals:
                service_type_id = self.env['fleet.service.type'].browse(vals['service_type_id'])
                if service_type_id and service_type_id.product_id:
                    vals['product_id'] = service_type_id.product_id.id
        records = super(FleetVehicleLogServices, self).create(vals_list)
        return records

    def action_view_invoice(self):
        invoices = self.mapped('invoice_id')
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
