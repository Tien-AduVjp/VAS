from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class FleetVehicleRevenue(models.Model):
    _name = 'fleet.vehicle.revenue'
    _inherit = ['fleet.vehicle.revenue', 'abstract.vehicle.cost.revenue']

    amount = fields.Monetary('Total Price')

    customer_id = fields.Many2one('res.partner', string="Customer")
    company_id = fields.Many2one(default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')
    created_from_invoice_line_id = fields.Many2one(help="A technical field to indicate that this revenue was created from an invoice line")

    @api.constrains('product_id', 'revenue_subtype_id')
    def _check_constrains_product(self):
        for r in self.filtered(lambda r: r.revenue_subtype_id.product_id and r.product_id):
            if r.revenue_subtype_id.product_id.id != r.product_id.id:
                raise ValidationError(_("The revenue must have the same product as its Type's product."
                                        " Otherwise, you must leave its Product field empty so that the"
                                        " Type's Product will be used."))

    @api.onchange('revenue_subtype_id')
    def _onchange_revenue_subtype_id(self):
        if self.revenue_subtype_id and self.revenue_subtype_id.product_id:
            self.product_id = self.revenue_subtype_id.product_id

    @api.model
    def get_product(self):
        return (self.product_id or self.revenue_subtype_id.product_id)

    def name_get(self):
        result = []
        for r in self:
            if r.revenue_subtype_id:
                result.append((r.id, '[%s] %s' % (r.name, r.revenue_subtype_id.name)))
            else:
                result.append((r.id, r.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('revenue_subtype_id.name', 'ilike', name), ('name', operator, name)]
        tags = self.search(domain + args, limit=limit)
        return tags.name_get()

    def action_view_invoice(self):
        invoices = self.mapped('invoice_id')
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _get_domain_for_gabage_cron(self):
        return [('created_from_invoice_line_id', '!=', False), ('invoice_line_id', '=', False)]

    @api.model
    def cron_garbage(self):
        garbage = self.search(self._get_domain_for_gabage_cron())
        if garbage:
            garbage.unlink()
        return True

    def _get_invoice_line_name(self):
        self.ensure_one()
        product_desc = self.product_id.description_sale and self.product_id.description_sale or ''
        return "%s\n%s" % (self.display_name, product_desc)

    def _get_account_id(self):
        self.ensure_one()
        ir_property_obj = self.env['ir.property']
        account_id = False

        # if revenue has product, get account from product settings
        if self.product_id:
            account_id = self.product_id.product_tmpl_id._get_product_accounts()['income']

        # otherwise. get the company property
        if not account_id:
            account_id = ir_property_obj.get('property_account_income_categ_id', 'product.category')

        if not account_id:
            if self.product_id:
                raise UserError(
                    _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, Settings menu.')
                    % (self.product_id.name,))
            else:
                raise UserError(
                    _("There is neither product defined for the revenue id: %d nor income account in product category property.")
                    % (self.id,))

        return account_id

    def _get_tax_ids(self, fiscal_position_id=None):
        self.ensure_one()
        taxes = False
        if self.product_id:
            taxes = self.product_id.taxes_id.filtered(lambda r: not self.company_id or r.company_id == self.company_id)
        if fiscal_position_id and taxes:
            taxes = fiscal_position_id.map_tax(taxes)
        return taxes

    def _prepare_invoice_line_data(self, fiscal_position_id=None):
        data = super(FleetVehicleRevenue, self)._prepare_invoice_line_data(fiscal_position_id)
        data.update({
            'fleet_vehicle_revenue_ids': [(6, 0, [self.id])],
            })
        return data
