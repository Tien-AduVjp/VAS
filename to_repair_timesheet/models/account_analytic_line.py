from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    ro_line = fields.Many2one('repair.fee', string='Repair Fees Line')

    @api.model
    def create(self, values):
        result = super(AccountAnalyticLine, self).create(values)
        result._repair_postprocess(values)
        if result.project_id:
            result._timesheet_postprocess(values)
        return result

    def write(self, values):
        # get current so lines for which update qty wil be required
        repair_order_lines = self.env['repair.fee']
        if 'ro_line' in values:
            repair_order_lines = self.sudo().mapped('ro_line')

        if self.sudo().filtered(lambda aal: aal.ro_line.product_id.invoice_policy == "delivery") and self.filtered(lambda timesheet: timesheet.timesheet_invoice_id):
            if any([field_name in values for field_name in ['unit_amount', 'employee_id', 'task_id', 'timesheet_revenue', 'ro_line', 'amount', 'date']]):
                raise UserError(_("Timesheet, that is linked to an invoice, cannot be updated or deleted. Please remove the invoice first."))

        result = super(AccountAnalyticLine, self).write(values)
        self._repair_postprocess(values, additional_ro_lines=repair_order_lines)
        self.filtered(lambda t: t.project_id)._timesheet_postprocess(values)
        return result

    def unlink(self):
        repair_order_lines = self.sudo().mapped('ro_line')

        if self.timesheet_invoice_id:
            raise UserError(_("Timesheet, that is linked to an invoice, cannot be updated or deleted. Please remove the invoice first."))

        res = super(AccountAnalyticLine, self).unlink()
        repair_order_lines.with_context(repair_analytic_force_recompute=True)._analytic_compute_delivered_quantity()
        return res

    @api.model
    def _timesheet_preprocess(self, values):
        values = super(AccountAnalyticLine, self)._timesheet_preprocess(values)
        # task implies so line
        if 'task_id' in values:
            task = self.env['project.task'].sudo().browse(values['task_id'])
            values['ro_line'] = task.repair_fee_line_id.id or values.get('ro_line', False)
        return values

#     def _timesheet_postprocess(self, values):
#         super(AccountAnalyticLine, self)._timesheet_postprocess(values)
#         sudo_self = self.sudo()  # this creates only one env for all operation that required sudo()
#         # (re)compute the theorical revenue
#         if any([field_name in values for field_name in ['ro_line']]):
#             sudo_self._timesheet_compute_theorical_revenue()
#         return values
#
#     def _timesheet_compute_theorical_revenue(self):
#         for timesheet in self:
#             values = timesheet._timesheet_compute_theorical_revenue_values()
#             timesheet.write(values)
#         return True
#
#
#     def _timesheet_compute_theorical_revenue_values(self):
#         values = {}
#         self.ensure_one()
#         timesheet = self
#
#         # find the timesheet UoM
#         timesheet_uom = timesheet.product_uom_id
#         if not timesheet_uom:  # fallback on default company timesheet UoM
#             timesheet_uom = self.env.company.project_time_mode_id
#
#         # default values
#         unit_amount = timesheet.unit_amount
#         ro_line = timesheet.ro_line
#         # set the revenue and billable type according to the product and the SO line
#         if timesheet.task_id and ro_line.product_id.type == 'service':
#             analytic_account = timesheet.account_id
#             # convert the unit of mesure into hours
#             repair_price_hour = ro_line.product_uom._compute_price(ro_line.price_unit, timesheet_uom)
#             repair_price = ro_line.repair_id.pricelist_id.currency_id.compute(repair_price_hour, analytic_account.currency_id)
#
#             # calculate the revenue on the timesheet
#             if ro_line.product_id.invoice_policy == 'delivery':
#                 values['timesheet_revenue'] = analytic_account.currency_id.round(unit_amount * repair_price)
#                 values['timesheet_invoice_type'] = 'billable_time' if ro_line.product_id.service_type == 'timesheet' else 'billable_fixed'
#             elif ro_line.product_id.invoice_policy == 'order' and ro_line.product_id.service_type == 'timesheet':
#                 quantity_hour = unit_amount
#                 if ro_line.product_uom.category_id == timesheet_uom.category_id:
#                     quantity_hour = ro_line.product_uom._compute_quantity(ro_line.product_uom_qty, timesheet_uom)
#                 # compute the total revenue the SO since we are in fixed price
#                 total_revenue_so = analytic_account.currency_id.round(quantity_hour * repair_price)
#                 # compute the total revenue already existing (without the current timesheet line)
#                 domain = [('ro_line', '=', ro_line.id)]
#                 if timesheet.ids:
#                     domain += [('id', 'not in', timesheet.ids)]
#                 analytic_lines = timesheet.search(domain)
#                 total_revenue_invoiced = sum(analytic_lines.mapped('timesheet_revenue'))
#                 # compute (new) revenue of current timesheet line
#                 values['timesheet_revenue'] = min(
#                     analytic_account.currency_id.round(unit_amount * ro_line.repair_id.pricelist_id.currency_id.compute(ro_line.price_unit, analytic_account.currency_id)),
#                     total_revenue_so - total_revenue_invoiced
#                 )
#                 values['timesheet_invoice_type'] = 'billable_fixed'
#                 # if the so line is already invoiced, and the delivered qty is still smaller than the ordered, then link the timesheet to the invoice
#                 if ro_line.invoice_status == 'invoiced':
#                     values['timesheet_invoice_id'] = ro_line.invoice_lines and ro_line.invoice_lines[0].invoice_id.id
#             elif ro_line.product_id.invoice_policy == 'order' and ro_line.product_id.service_type != 'timesheet':
#                 values['timesheet_invoice_type'] = 'billable_fixed'
#
#         return values

    @api.model
    def _repair_get_fields_delivered_qty(self):
        """ Returns a list with the field impacting the delivered quantity on RO line. """
        return ['ro_line', 'unit_amount', 'product_uom_id']

    def _repair_postprocess(self, values, additional_ro_lines=None):
        if 'so_line' not in values:  # allow to force a False value for so_line
            # only take the AAL from expense or vendor bill, meaning having a negative amount
            self.filtered(lambda aal: aal.amount <= 0).with_context(repair_analytic_norecompute=True)._repair_determine_order_line()

        if any(field_name in values for field_name in self._repair_get_fields_delivered_qty()):
            if not self._context.get('repair_analytic_norecompute'):
                ro_lines = self.sudo().filtered(lambda aal: aal.ro_line).mapped('ro_line')
                if additional_ro_lines:
                    ro_lines |= additional_ro_lines
                ro_lines.sudo()._analytic_compute_delivered_quantity()

    # NOTE JEM: thoses method are used in vendor bills to reinvoice at cost (see test `test_cost_invoicing`)
    # some cleaning are still necessary

    def _repair_get_invoice_price(self):
        price_unit = abs(self.amount / self.unit_amount)
        return price_unit

    def _repair_prepare_repair_order_line_values(self, order, price):
        self.ensure_one()
        fpos = order.partner_id.property_account_position_id
        taxes = fpos.map_tax(self.product_id.taxes_id, self.product_id, order.partner_id)

        return {
            'repair_id': order.id,
            'name': self.name,
            'price_unit': price,
            'tax_id': [x.id for x in taxes],
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': 0.0,
            'qty_delivered': self.unit_amount,
        }

    def _repair_determine_order(self):
        mapping = {}
        self = self.sudo().filtered(lambda aal: not aal.ro_line and aal.product_id and aal.product_id.expense_policy != 'no')
        orders = self.env['repair.order'].search([('analytic_account_id', 'in', self.account_id.ids)])
        for r in self:
            repair_order = orders.filtered(lambda o: o.analytic_account_id == r.account_id and o.state not in ('draft', 'cancel'))[:1]
            if not repair_order:
                repair_order = orders.filtered(lambda o: o.analytic_account_id == r.account_id)[:1]
            if not repair_order:
                continue
            mapping[r.id] = repair_order
        return mapping

    def _repair_determine_order_line(self):
        # determine SO : first SO open linked to AA
        repair_order_map = self._repair_determine_order()
        # determine so line
        for r in self.sudo().filtered(lambda aal: not aal.ro_line and aal.product_id and aal.product_id.expense_policy != 'no'):
            repair_order = repair_order_map.get(r.id)
            if not repair_order:
                continue

            if repair_order.state in ['draft', 'cancel']:
                raise UserError(_('The Repair Order %s linked to the Analytic Account must be validated before registering expenses.') % repair_order.name)

            price = r._repair_get_invoice_price()
            ro_line = None
            if r.product_id.expense_policy == 'sales_price' and r.product_id.invoice_policy == 'delivery':
                ro_line = self.env['repair.fee'].search([
                    ('repair_id', '=', repair_order.id),
                    ('price_unit', '=', price),
                    ('product_id', '=', self.product_id.id)
                ], limit=1)

            if not ro_line:
                # generate a new SO line
                if repair_order.state in ['draft', 'cancel']:
                    raise UserError(_('The Repair Order %s linked to the Analytic Account must be validated before registering expenses.') % repair_order.name)
                ro_line_values = r._repair_prepare_repair_order_line_values(repair_order, price)
                ro_line = self.env['repair.fee'].create(ro_line_values)
#                 ro_line._compute_tax_id()
            else:
                ro_line.write({'qty_delivered': ro_line.qty_delivered + r.unit_amount})

            if ro_line:  # if so line found or created, then update AAL (this will trigger the recomputation of qty delivered on SO line)
                r.with_context(repair_analytic_norecompute=True).write({'ro_line': ro_line.id})
