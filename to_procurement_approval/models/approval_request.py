import threading
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    procurement_request_line_ids = fields.One2many('procurement.request.line', 'approval_id', readonly=True, states={'draft':[('readonly', False)]}, string='Procurement Request Lines',
                                    help="List of products associated to this procurement request")
    # TODOs: handle to avoid conflict with module to_stock_product_allocation_approval:
    # pickings_id = fields.Many2many...
    # picking_count = = fields.Integer
    picking_ids = fields.One2many('stock.picking', 'approval_request_id', string='Transfers',
                                  compute='_compute_picking_ids',groups='stock.group_stock_user',
                                  help="List of transfers associated to this procurement request", store=True)
    pickings_count = fields.Integer(string='Transfers count', compute="_compute_pickings_count",groups='stock.group_stock_user')
    purchase_order_ids = fields.Many2many('purchase.order', 'procurement_requests_purchase_order_rel', 'approval_request_id', 'purchase_order_id',
                                compute='_compute_purchase_order_ids', help="List of purchase orders associated to this procurement request",
                                groups='purchase.group_purchase_user',string='Purchase Orders', store=True)
    purchase_orders_count = fields.Integer(string="Purchase order count", compute='_compute_purchase_orders_count',groups='purchase.group_purchase_user')
    procurement_group_ids = fields.One2many('procurement.group', 'approval_request_id', string='Procurement Group', help="List of procurement group associated to this procurement request")
    procurement_groups_count = fields.Integer(string='Procurement Groups Count', compute='_compute_procurement_groups_count')

    def _compute_procurement_groups_count(self):
        for r in self:
            r.procurement_groups_count = len(r.procurement_group_ids)

    @api.depends('procurement_group_ids.stock_move_ids')
    def _compute_picking_ids(self):
        all_picking_ids = self.env['stock.picking'].search([('group_id', 'in', self.mapped('procurement_group_ids').ids)])
        for r in self:
            picking_ids = all_picking_ids.filtered(lambda p: p.group_id.id in r.procurement_group_ids.ids)
            r.picking_ids = [(6, 0, picking_ids.ids)]

    def _compute_pickings_count(self):
        picking_data = self.env['stock.picking'].read_group([('approval_request_id', 'in', self.ids)], ['approval_request_id'], ['approval_request_id'])
        mapped_data = dict([(p['approval_request_id'][0], p['approval_request_id_count']) for p in picking_data])
        for r in self:
            r.pickings_count = mapped_data.get(r.id, 0)

    @api.depends('procurement_group_ids')
    def _compute_purchase_order_ids(self):
        all_purchase_order_ids = self.env['purchase.order'].search([('group_id', 'in', self.mapped('procurement_group_ids').ids)])
        for r in self:
            purchase_order_ids = all_purchase_order_ids.filtered(lambda p: p.group_id.id in r.procurement_group_ids.ids)
            purchase_order_ids = purchase_order_ids | r.purchase_order_ids if purchase_order_ids else r.purchase_order_ids
            r.purchase_order_ids = [(6, 0, purchase_order_ids.ids)]

    def _compute_purchase_orders_count(self):
        for r in self:
            r.purchase_orders_count = len(r.purchase_order_ids)

    def _get_validated_product_qty_lines(self, service=False):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        if service:
            return self.procurement_request_line_ids.filtered(lambda l: not float_is_zero(l.quantity, precision_digits=precision) and l.type == 'service' and l.state == 'validate')
        return self.procurement_request_line_ids.filtered(lambda l: not float_is_zero(l.quantity, precision_digits=precision) and l.type != 'service' and l.state == 'validate')

    def _prepare_procurement_group_data(self, partner_id):
        return {
            'partner_id': partner_id.id,
            'name': self.name,
            'approval_request_id': self.id,
            }

    def action_confirm(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for r in self:
            if r.approval_type_id.type == 'procurement' and all(float_is_zero(l.quantity, precision_digits=precision) for l in r.procurement_request_line_ids):
                raise UserError(_("You must have at least one non-zero quantity line to submit for approval '%s'."
                                        " Submitting a zero-quanity line does not make sense.") % r.display_name)
        return super(ApprovalRequest, self).action_confirm()

    def action_validate(self):
        super(ApprovalRequest, self).action_validate()
        for r in self.filtered(lambda line: line.state == 'validate' and line.type == 'procurement'):
            if any(not line.product_id for line in r.procurement_request_line_ids):
                raise UserError(_('All lines must be have product.'))
            if not r.procurement_request_line_ids:
                raise UserError(_("Please add some items to procurement."))
            else:
                product_qty_lines = r._get_validated_product_qty_lines()
                if product_qty_lines:
                    r.run_procurement(product_qty_lines)
                service_product_qty_lines = r._get_validated_product_qty_lines(service=True)
                if service_product_qty_lines:
                    r.buy_product_service_type(service_product_qty_lines)

    def run_procurement(self, line_ids):
        procurement_group_id = self.env['procurement.group'].create(self._prepare_procurement_group_data(self.env.user.partner_id))
        line_ids.write({'procurement_group_id': procurement_group_id.id})
        line_ids.launch_procurement()

    def buy_product_service_type(self, line_ids):
        self.ensure_one()
        origins = set([p.name for p in self])
        schedule_date = (self.date - relativedelta(days=self.company_id.po_lead))
        PurchaseOrder = self.env['purchase.order']
        for line_id in line_ids:
            supplier = line_id.product_id.with_company(self.company_id)._select_seller(
                partner_id=False,
                quantity=line_id.quantity,
                date=schedule_date,
                uom_id=line_id.uom_id)

            if not supplier:
                msg = _("There is no matching vendor price to generate the purchase order for product '%s' (no vendor defined, minimum quantity not reached, dates not valid, ...). Go on the product form and complete the list of vendors.") % (line_id.product_id.display_name)
                raise UserError(msg)

            partner_id = supplier.name
            picking_type_id = self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)
            po = PurchaseOrder.sudo().search([('partner_id', '=', partner_id.id),
            ('state', '=', 'draft'), ('picking_type_id', '=', picking_type_id.id),
            ('company_id', '=', self.company_id.id)], limit=1)
            if not po:
                vals = self._prepare_purchase_order(self.company_id, origins, supplier, schedule_date, picking_type_id)
                po = PurchaseOrder.with_company(self.company_id).sudo().create(vals)
            else:
                if po.origin:
                    origins = origins - set(po.origin.split(', '))
                    if origins:
                        po.write({'origin': po.origin + ', ' + ', '.join(origins)})
                else:
                    po.write({'origin': ', '.join(origins)})
            self.purchase_order_ids = [(4, po.id)]
            po_line_values = self._prepare_purchase_order_line(line_id.product_id, line_id.quantity, line_id.uom_id, self.company_id, supplier, po)
            self.env['purchase.order.line'].sudo().create(po_line_values)

    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, supplier, po):
        procurement_uom_po_qty = product_uom._compute_quantity(product_qty, product_id.uom_po_id)
        partner = supplier.name
        taxes = product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(taxes, product_id, partner) if fpos else taxes
        if taxes_id:
            taxes_id = taxes_id.filtered(lambda x: x.company_id.id == company_id.id)

        price_unit = self.env['account.tax']._fix_tax_included_price_company(supplier.price, product_id.supplier_taxes_id, taxes_id, company_id) if supplier else 0.0
        if price_unit and supplier and po.currency_id and supplier.currency_id != po.currency_id:
            price_unit = supplier.currency_id._convert(
                price_unit, po.currency_id, po.company_id, po.date_order or fields.Date.context_today(self))

        product_lang = product_id.with_prefetch().with_context(
            lang=partner.lang,
            partner_id=partner.id,
        )
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase

        date_planned = self.env['purchase.order.line']._get_date_planned(supplier, po=po)
        return {
            'name': name,
            'product_qty': procurement_uom_po_qty,
            'product_id': product_id.id,
            'product_uom': product_id.uom_po_id.id,
            'price_unit': price_unit,
            'date_planned': date_planned,
            'taxes_id': [(6, 0, taxes_id.ids)],
            'order_id': po.id,
        }

    def _prepare_purchase_order(self, company_id, origins, supplier, schedule_date, picking_type_id):
        partner_id = supplier.name
        purchase_date = schedule_date - relativedelta(days=int(supplier.delay))
        fpos = self.env['account.fiscal.position'].with_company(company_id).get_fiscal_position(partner_id.id)
        return {
            'partner_id': partner_id.id,
            'user_id': False,
            'picking_type_id': picking_type_id.id,
            'company_id': company_id.id,
            'currency_id': partner_id.with_company(company_id).property_purchase_currency_id.id or company_id.currency_id.id,
            'dest_address_id': partner_id.id,
            'origin': ', '.join(origins),
            'payment_term_id': partner_id.with_company(company_id).property_supplier_payment_term_id.id,
            'date_order': purchase_date,
            'fiscal_position_id': fpos
        }

    def _get_picking_type(self, company_id):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return picking_type[:1]

    def action_view_procurement_groups(self):
        self.ensure_one()

        action = self.env['ir.actions.act_window']._for_xml_id('to_procurement_approval.action_procurement_group_view')
        action['context'] = dict(self._context, create=False)
        if self.procurement_groups_count == 1:
            res = self.env.ref('stock.procurement_group_form_view', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = self.procurement_group_ids.id
        else:
            action['domain'] = "[('approval_request_id', '=', %s)]" % self.id
        return action

    def action_view_stock_pickings(self):
        self.ensure_one()

        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        action['context'] = dict(self._context, create=False)
        if self.pickings_count == 1:
            res = self.env.ref('stock.view_picking_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = self.picking_ids.id
        else:
            action['domain'] = "[('id', 'in', %s)]" % self.picking_ids.ids
        return action

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_form_action')
        action['context'] = dict(self._context, create=False)
        if self.purchase_orders_count == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = self.purchase_order_ids.id
        else:
            action['domain'] = "[('id', 'in', %s)]" % self.purchase_order_ids.ids
        return action
