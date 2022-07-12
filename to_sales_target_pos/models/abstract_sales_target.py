from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AbstractSalesTarget(models.AbstractModel):
    _inherit = 'abstract.sales.target'

    non_invoiced_pos_order_ids = fields.Many2many('pos.order','abstract_sales_target_pos_order_non', string='Non-Invoiced PoS Orders', compute='_compute_pos_order_ids', store=True,
                                                  help="The PoS Orders that are related to this target and in the state of either Paid or Done")
    non_invoiced_pos_orders_count = fields.Integer(string='Non-Invoiced PoS Orders Count', compute='_compute_non_invoiced_pos_orders_count', store=True)
    invoiced_pos_order_ids = fields.Many2many('pos.order','abstract_sales_target_pos_order', string='Invoiced PoS Orders', compute='_compute_pos_order_ids', store=True,
                                              help="The PoS Orders that are related to this target and in the state of Invoiced")
    invoiced_pos_orders_count = fields.Integer(string='Invoiced PoS Orders Count', compute='_compute_invoiced_pos_orders_count', store=True)

    non_invoiced_pos_sales_total = fields.Float(string='Non-Invoiced PoS Sales Total', compute='_compute_non_invoiced_pos_sales_total', store=True,
                                                help="Total sales amount recorded in Point of Sales application without an invoice issued")
    invoiced_pos_sales_total = fields.Float(string='Invoiced PoS Sales Total', compute='_compute_invoiced_pos_sales_total', store=True,
                                            help="Total invoiced sales amount recorded in Point of Sales application")

    pos_sales_total = fields.Float(string='PoS Sales Total', compute='_compute_pos_sales_total', store=True,
                                   help="Total sales amount recorded in Point of Sales application, including invoiced and uninvoiced sales")

    pos_sales_target_reached = fields.Float(string='PoS & Sales Target Reached', compute='_compute_pos_sales_target_reached', store=True,
                                            help="The percentage of target completion according to the PoS Sales data, which is computed with the formula:"
                                            "Sales Target Reached = 100.0 * PoS Sales Total / Target")

    def _get_pos_orders(self):
        raise ValidationError(_("The method `_get_pos_orders` has not been implemented for the model '%s'.") % self._name)

    def _compute_pos_order_ids(self):
        for r in self:
            if r.state in ('approved', 'done'):
                non_invoiced_pos_order_ids, invoiced_pos_order_ids = r._get_pos_orders()
                r.non_invoiced_pos_order_ids = non_invoiced_pos_order_ids
                r.invoiced_pos_order_ids = invoiced_pos_order_ids
            else:
                r.non_invoiced_pos_order_ids = []
                r.invoiced_pos_order_ids = []

    @api.depends('non_invoiced_pos_order_ids')
    def _compute_non_invoiced_pos_orders_count(self):
        for r in self:
            r.non_invoiced_pos_orders_count = len(r.non_invoiced_pos_order_ids)

    @api.depends('non_invoiced_pos_order_ids')
    def _compute_non_invoiced_pos_sales_total(self):
        ReportPosOrder = self.env['report.pos.order'].sudo()
        for r in self:
            report_pos_order_line_ids = ReportPosOrder.search([('order_id', 'in', r.non_invoiced_pos_order_ids.ids)])
            r.non_invoiced_pos_sales_total = sum(report_pos_order_line_ids.mapped('price_total'))

    @api.depends('invoiced_pos_order_ids')
    def _compute_invoiced_pos_orders_count(self):
        for r in self:
            r.invoiced_pos_orders_count = len(r.invoiced_pos_order_ids)

    @api.depends('invoiced_pos_order_ids')
    def _compute_invoiced_pos_sales_total(self):
        ReportPosOrder = self.env['report.pos.order'].sudo()
        for r in self:
            report_pos_order_line_ids = ReportPosOrder.search([('order_id', 'in', r.invoiced_pos_order_ids.ids)])
            r.invoiced_pos_sales_total = sum(report_pos_order_line_ids.mapped('price_total'))

    @api.depends('non_invoiced_pos_sales_total', 'invoiced_pos_sales_total')
    def _compute_pos_sales_total(self):
        for r in self:
            r.pos_sales_total = r.non_invoiced_pos_sales_total + r.invoiced_pos_sales_total

    @api.depends('target', 'pos_sales_total')
    def _compute_pos_sales_target_reached(self):
        for r in self:
            if r._is_zero_target():
                r.pos_sales_target_reached = 0.0
            else:
                r.pos_sales_target_reached = 100.0 * r.pos_sales_total / r.target

    @api.depends('sales_invoiced', 'non_invoiced_pos_sales_total')
    def _compute_all_channel_sales_total(self):
        for r in self:
            r.sales_total = r.sales_invoiced + r.non_invoiced_pos_sales_total

    def action_view_non_invoiced_pos_orders(self):
        action = self.env['ir.actions.act_window']._for_xml_id('point_of_sale.action_pos_pos_form')

        order_ids = self.non_invoiced_pos_order_ids
        orders_count = len(order_ids)
        # choose the view_mode accordingly
        if orders_count != 1:
            action['domain'] = "[('id', 'in', " + str(order_ids.ids) + ")]"
        elif orders_count == 1:
            res = self.env.ref('point_of_sale.view_pos_pos_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = order_ids.id
        return action

    def action_view_invoiced_pos_orders(self):
        action = self.env['ir.actions.act_window']._for_xml_id('point_of_sale.action_pos_pos_form')

        order_ids = self.invoiced_pos_order_ids
        orders_count = len(order_ids)
        # choose the view_mode accordingly
        if orders_count != 1:
            action['domain'] = "[('id', 'in', " + str(order_ids.ids) + ")]"
        elif orders_count == 1:
            res = self.env.ref('point_of_sale.view_pos_pos_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = order_ids.id
        return action
