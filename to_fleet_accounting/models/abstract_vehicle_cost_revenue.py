from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class FleetVehicleCostRevenue(models.AbstractModel):
    _name = 'abstract.vehicle.cost.revenue'
    _description = "Share business logics between vehicle's cost and revenue models"

    product_id = fields.Many2one('product.product', string='Invoiceable Product', index=True,
                                 help="The product to be used when invoicing the vehicle cost")
    invoice_line_id = fields.Many2one('account.move.line', string='Invoice Line', readonly=True, ondelete='set null', index=True, copy=False)

    invoice_id = fields.Many2one('account.move', string='Invoice Ref.', related='invoice_line_id.move_id', readonly=True, store=True, index=True, copy=False)

    created_from_invoice_line_id = fields.Many2one('account.move.line', string='Created From Invoice Line', readonly=True, ondelete='cascade', copy=False,
                                                   help="A technical field to indicate that this record was created from an invoice line")

    company_id = fields.Many2one('res.company', string='Company')
    currency_id = fields.Many2one('res.currency', string='Currency', store=True)
    amount = fields.Monetary()

    def _get_account_id(self):
        self.ensure_one()
        raise ValidationError(_("The method _get_account_id has not been implemented for the model %s") % (self._name,))

    def _get_analytic_account(self):
        return self.vehicle_id.analytic_account_id or self.invoice_line_id.analytic_account_id

    def _get_analytic_tags(self):
        return self.invoice_line_id.analytic_tag_ids

    def _get_tax_ids(self, fiscal_position_id=None):
        self.ensure_one()
        raise ValidationError(_("The method _get_tax_ids has not been implemented for the model %s") % (self._name,))

    def _get_invoice_line_name(self):
        self.ensure_one()
        raise ValidationError(_("The method _get_invoice_line_name has not been implemented for the model %s") % (self._name,))

    def _guess_product(self):
        product_obj = self.env['product.product']
        return self.product_id or product_obj.search([('name', '=', self.name)]) or product_obj.search([('name', 'ilike', '%' + self.name + '%')])

    def _prepare_invoice_line_data(self, fiscal_position_id=None):
        self.ensure_one()
        account_id = self._get_account_id()

        if not account_id:
            raise UserError(_("There is no required account defined for this operation."))

        taxes = self._get_tax_ids(fiscal_position_id)

        product = self._guess_product()

        data = {
            'name': self._get_invoice_line_name(),
            'ref': self._get_invoice_line_name(),
            'product_id': product and product.id or False,
            'account_id': account_id.id,
            'price_unit': self.amount,
            'quantity': 1.0,
            'discount': 0.0,
            'product_uom_id': self.product_id and self.product_id.uom_id.id or False,
            'product_id': self.product_id and self.product_id.id or False,
            'tax_ids': taxes and [(6, 0, taxes.ids)] or [],
            }

        return data

    def _prepare_invoice_lines_data(self, fiscal_position_id=None):
        vals_list = []
        for r in self:
            vals_list.append(r._prepare_invoice_line_data(fiscal_position_id))
        return vals_list

    @api.constrains('vehicle_id', 'vehicle_id', 'company_id')
    def _check_company_constrains(self):
        for r in self:
            if r.vehicle_id.company_id and r.company_id:
                if r.company_id.id != r.vehicle_id.company_id.id:
                    raise ValidationError(_("You are about create the cost of the vehicle '%s' for the company '%s'"
                                            " which is not the same as the vehicle's which is %s")
                                          % (r.vehicle_id.name, r.company_id.name, r.vehicle_id.company_id.name))
