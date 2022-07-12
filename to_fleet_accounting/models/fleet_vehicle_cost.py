from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class FleetVehicleCost(models.Model):
    _name = 'fleet.vehicle.cost'
    _inherit = ['abstract.vehicle.cost.revenue', 'fleet.vehicle.cost']

    vendor_id = fields.Many2one('res.partner', string="Service Vendor")

    created_from_invoice_line_id = fields.Many2one(help="A technical field to indicate that this cost was created from an invoice line", copy=False)

    invoiceable = fields.Boolean(string='Invoiceable', compute='_compute_invoiceable', store=True, default=False, copy=False)

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

        # if cost has product specified, get account from product settings
        if self.product_id:
            account_id = self.product_id.product_tmpl_id._get_product_accounts()['expense']

        # otherwise. get the company property
        if not account_id:
            account_id = ir_property_obj.get('property_account_expense_categ_id', 'product.category')

        if not account_id:
            if self.product_id:
                raise UserError(
                    _('There is no expense account defined for this product: "%s". You may have to install a chart of account from Accounting app, Settings menu.')
                    % (self.product_id.name,))
            else:
                raise UserError(
                    _("There is neither product defined for the cost id: %d nor expense account in product category property.")
                    % (self.id,))

        return account_id

    def _prepare_analytic_line_data(self):
        self.ensure_one()
        analytic_account = self._get_analytic_account()
        if not analytic_account:
            raise ValidationError(_("There is no analytic account specified for the vehicle %s") % self.vehicle_id.display_name)
        product = self.get_product()
        return {
            'name': self.name,
            'account_id': analytic_account.id,
            'tag_ids': [(6, 0, self._get_analytic_tags().ids)],
            'date': self.date or self.invoice_id.date,
            'company_id': self.company_id.id,
            'amount':-1 * self.amount,
            'partner_id': self.vendor_id and self.vendor_id.id or False,
            'vehicle_cost_id': self.id,
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
        data = super(FleetVehicleCost, self)._prepare_invoice_line_data(fiscal_position_id)
        data.update({
            'fleet_vehicle_cost_ids': [(6, 0, [self.id])],
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

    @api.constrains('product_id', 'cost_subtype_id')
    def _check_constrains_product(self):
        for r in self:
            if r.cost_subtype_id:
                if r.cost_subtype_id.product_id and r.product_id:
                    if r.cost_subtype_id.product_id.id != r.product_id.id:
                        raise ValidationError(_("The cost must have the same product as its Type's product."
                                                " Otherwise, you must leave its Product field empty so that the"
                                                " Type's Product will be used."))

    @api.constrains('cost_ids', 'cost_ids')
    def _check_constrains_cost_ids_currency(self):
        for r in self:
            if r.currency_id and r.cost_ids:
                if any(cost.currency_id.id != r.currency_id.id for cost in r.cost_ids):
                    raise ValidationError(_("Child Costs must have the same currency as its parent's"))

    @api.onchange('cost_subtype_id')
    def _onchange_cost_subtype_id(self):
        if self.cost_subtype_id and self.cost_subtype_id.product_id:
            self.product_id = self.cost_subtype_id.product_id

    def get_product(self):
        return self.invoice_line_id.product_id or self.product_id or self.cost_subtype_id.product_id or False

    def name_get(self):
        result = []
        for r in self:
            if r.cost_subtype_id:
                result.append((r.id, '[%s] %s' % (r.name, r.cost_subtype_id.name)))
            else:
                result.append((r.id, r.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('cost_subtype_id.name', 'ilike', name), ('name', operator, name)]
        tags = self.search(domain + args, limit=limit)
        return tags.name_get()

    def write(self, vals):
        res = super(FleetVehicleCost, self).write(vals)
        child_vals = {}
        if 'currency_id' in vals:
            child_vals['currency_id'] = vals['currency_id']
        if 'vendor_id' in vals:
            child_vals['vendor_id'] = vals['vendor_id']
        for r in self:
            if r.parent_id:
                if 'currency_id' in vals:
                    if r.parent_id.currency_id:
                        if r.parent_id.currency_id.id != r.currency_id.id:
                            raise ValidationError(_("The cost %s has parent, hence, cannot change currency.")
                                                  % (r.display_name,))

                if 'vendor_id' in vals:
                    if r.parent_id.vendor_id:
                        if r.parent_id.vendor_id.id != r.vendor_id.id:
                            raise ValidationError(_("The cost %s has parent, hence, cannot change its vendor.")
                                                  % (r.display_name,))

            if bool(child_vals):
                for cost in r.cost_ids:
                    cost.write(child_vals)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'parent_id' in vals.keys():
                parrent_currency_id = self.browse(vals['parent_id']).currency_id
                if parrent_currency_id:
                    vals['currency_id'] = parrent_currency_id.id
            if 'cost_subtype_id' in vals:
                cost_subtype_id = self.env['fleet.service.type'].browse(vals['cost_subtype_id'])
                if cost_subtype_id and cost_subtype_id.product_id:
                    vals['product_id'] = cost_subtype_id.product_id.id
        records = super(FleetVehicleCost, self).create(vals_list)
        for rec in records:
            rec.cost_ids.write({
                'currency_id': rec.currency_id.id,
                })
        return records

    def action_view_invoice(self):
        invoices = self.mapped('invoice_id')
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.model
    def cron_garbage(self):
        garbage = self.search([('created_from_invoice_line_id', '!=', False), ('invoice_line_id', '=', False)])
        if garbage:
            garbage.unlink()
        return True

