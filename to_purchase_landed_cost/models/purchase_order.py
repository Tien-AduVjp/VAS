from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def get_default_landed_cost_products(self):
        if not self.order_line:
            return []

        prod_tmpl_ids = self.order_line.filtered(lambda l: l.product_id.type == 'product').mapped('product_id.product_tmpl_id')
        landed_cost_product_ids = prod_tmpl_ids.mapped('product_landed_cost_ids').filtered(lambda l: l.auto_purchase == True).mapped('product_id')
        return landed_cost_product_ids

    purchase_landed_cost_ids = fields.One2many('purchase.landed.cost', 'order_id',
                                               readonly=False, states={'sent': [('readonly', True)],
                                                                       'to approve': [('readonly', True)],
                                                                       'purchase': [('readonly', True)],
                                                                       'done': [('readonly', True)],
                                                                       'cancel': [('readonly', True)]},
                                               string='Purchase Landed Costs')

    landed_costs_for_po_ids = fields.Many2many('purchase.order', 'landed_cost_po_po_rel', 'order_id', 'landed_cost_order_id',
                                               string='Landed Costs for', compute='_compute_landed_costs_for_po_ids', store=True,
                                               copy=False,
                                               help="Store Purchase Orders from which this order was generated as landed cost purchase order")
    landed_cost_po_ids = fields.Many2many('purchase.order', 'landed_cost_po_po_rel', 'landed_cost_order_id', 'order_id',
                                          readonly=True,
                                          copy=False,
                                          string='Landed Costs Orders')

    landed_cost_po_count = fields.Integer(string='Landed Cost Purchases', compute='_compute_landed_cost_po_count')

    stock_valuation_adjustment_lines_ids = fields.One2many('stock.valuation.adjustment.lines', 'purchase_order_id',
                                                           domain=[('state', '=', 'done')], readonly=True,
                                                           string='Landed Cost Adjustments')

    stock_landed_cost_ids = fields.Many2many('stock.landed.cost', string='Landed Costs', compute='_compute_stock_landed_cost_ids', store=True, copy=False)
    landed_costs_count = fields.Integer(string='Landed Costs Count', compute='_compute_landed_costs_count')

    @api.depends('stock_valuation_adjustment_lines_ids', 'stock_valuation_adjustment_lines_ids.cost_id', 'stock_valuation_adjustment_lines_ids.state')
    def _compute_stock_landed_cost_ids(self):
        for r in self:
            if r.stock_valuation_adjustment_lines_ids:
                stock_landed_cost_ids = r.stock_valuation_adjustment_lines_ids.mapped('cost_id')
                if stock_landed_cost_ids:
                    r.stock_landed_cost_ids = stock_landed_cost_ids.ids

    def _compute_landed_costs_count(self):
        for r in self:
            r.landed_costs_count = len(r.stock_landed_cost_ids)

    def _compute_landed_cost_po_count(self):
        for r in self:
            r.landed_cost_po_count = len(r.landed_cost_po_ids)

    @api.depends('order_line', 'order_line.landed_cost_for_po_ids')
    def _compute_landed_costs_for_po_ids(self):
        for r in self:
            landed_cost_for_po_ids = r.order_line.mapped('landed_cost_for_po_ids') - r
            r.landed_costs_for_po_ids = [(6, 0, landed_cost_for_po_ids.ids)]

    @api.model
    def _prepare_purchase_landed_cost_data(self, product_id):
        data = {
            'order_id': self.id,
            'product_id': product_id.id,
            'date_order': self.date_order,
            'product_uom_qty': 1.0,
            'product_uom_id': product_id.uom_po_id and product_id.uom_po_id.id or product_id.uom_id.id,
            }
        return data

    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        res = super(PurchaseOrder, self).copy(default=default)

        res._onchange_order_line()
        return res

    @api.onchange('order_line')
    def _onchange_order_line(self):
        purchase_landed_cost_ids = self.env['purchase.landed.cost']
        for product_id in self.get_default_landed_cost_products():
            new_line = purchase_landed_cost_ids.new(self._prepare_purchase_landed_cost_data(product_id))
            purchase_landed_cost_ids += new_line
        self.purchase_landed_cost_ids = purchase_landed_cost_ids

    @api.model
    def _create_landed_cost_po(self):
        big_dict = {}
        for line in self.purchase_landed_cost_ids:
            seller_id = line.get_seller()
            if not seller_id:
                raise ValidationError(_("Could not find vendor for the product '%s'. Please consider to specify one."
                                        " Otherwise, you should remove it from the Purchase Landed Cost lines")
                                        % (line.product_id.display_name,))
            if seller_id.name not in big_dict:
                big_dict[seller_id.name] = {seller_id: self.env['purchase.landed.cost']}
            elif seller_id not in big_dict[seller_id.name]:
                big_dict[seller_id.name].update({seller_id: self.env['purchase.landed.cost']})
            big_dict[seller_id.name][seller_id] += line

        PO = self.env['purchase.order']
        OrderLine = self.env['purchase.order.line']
        for vendor_id, seller_purchase_landed_cost_ids in big_dict.items():
            for seller_id, purchase_landed_cost_ids in seller_purchase_landed_cost_ids.items():
                picking_type_ids = purchase_landed_cost_ids.mapped('picking_type_id')
                for picking_type_id in picking_type_ids:
                    po_id = self.search([
                        ('state', 'in', ('draft', 'sent')),
                        ('currency_id', '=', seller_id.currency_id.id),
                        ('picking_type_id', '=', picking_type_id.id),
                        '|', ('partner_id', '=', vendor_id.id), ('partner_id.commercial_partner_id', '=', vendor_id.commercial_partner_id.id)], limit=1)
                    if not po_id:
                        po_id = PO.create({
                            'name':'New',
                            'partner_id': vendor_id.id,
                            'currency_id': seller_id.currency_id.id,
                            'date_order': purchase_landed_cost_ids[0].date_order,
                            'group_id': self.group_id.id,
                            })
                    order_line_ids = po_id.order_line
                    for cost_id in purchase_landed_cost_ids:
                        new_line = OrderLine.new(cost_id._prepare_po_line_data())
                        new_line._onchange_quantity()
                        order_line_ids += new_line
                    po_id.order_line = order_line_ids

    def button_approve(self, force=False):
        for r in self:
            for landed_cost in r.purchase_landed_cost_ids:
                if not landed_cost.date_order:
                    raise ValidationError(_("In the request for quotation %s, landed cost product '%s' has no scheduled order date. "
                                            "So, it is not possible to create a purchase order for the landed cost products. Please update this scheduled order date.")
                                          % (r.display_name, landed_cost.product_id.display_name))
            r._create_landed_cost_po()
        res = super(PurchaseOrder, self).button_approve(force=force)
        return res

    def button_cancel(self):
        super(PurchaseOrder, self).button_cancel()
        landed_cost_ol_ids = self.env['purchase.order.line'].search([('landed_cost_for_po_ids', 'in', self.ids)]).filtered(lambda l: l.order_id.state == 'draft' or l.order_id.id in self.ids)
        landed_cost_po_ids = landed_cost_ol_ids.mapped('order_id')
        landed_cost_ol_ids.unlink()
        can_delete_po_ids = landed_cost_po_ids.filtered(lambda po: not po.order_line)
        if can_delete_po_ids:
            can_delete_po_ids.button_cancel()
            can_delete_po_ids.unlink()

    def action_view_landed_cost_po(self):
        action = self.env['ir.actions.act_window']._for_xml_id('to_purchase_landed_cost.landed_cost_purchase_order_action')

        action.pop('id', None)
        action['context'] = {}
        landed_cost_po_ids = sum([order.landed_cost_po_ids.ids for order in self], [])
        # choose the view_mode accordingly
        if len(landed_cost_po_ids) > 1:
            action['domain'] = "[('id','in',[" + ','.join(map(str, landed_cost_po_ids)) + "])]"
        elif len(landed_cost_po_ids) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = landed_cost_po_ids and landed_cost_po_ids[0] or False
        return action

    def action_view_landed_costs(self):
        action = self.env['ir.actions.act_window']._for_xml_id('to_purchase_landed_cost.po_landed_cost_action')

        action.pop('id', None)
        action['context'] = {}
        stock_landed_cost_ids = sum([order.stock_landed_cost_ids.ids for order in self], [])
        # choose the view_mode accordingly
        if len(stock_landed_cost_ids) > 1:
            action['domain'] = "[('id','in',[" + ','.join(map(str, stock_landed_cost_ids)) + "])]"
        elif len(stock_landed_cost_ids) == 1:
            res = self.env.ref('stock_landed_cost.view_stock_landed_cost_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = stock_landed_cost_ids and stock_landed_cost_ids[0] or False
        return action
