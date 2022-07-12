from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    
    invoice_ids = fields.Many2many('account.move', string='Vendor Bills', compute='_compute_invoice_ids', store=True)
    should_wait_for_lc_invoice = fields.Boolean('Should Wait for Landed Cost Invoices', compute='_compute_should_wait_for_lc_invoice')

    @api.depends('picking_ids')
    def _compute_should_wait_for_lc_invoice(self):
        for r in self:
            # users may not have access right to po
            landed_cost_po_ids = self.picking_ids.sudo().mapped('purchase_id.landed_cost_po_ids')
            if any(po.state != 'cancel' or po.invoice_status == 'to invoice' for po in landed_cost_po_ids):
                r.should_wait_for_lc_invoice = True
            else:
                r.should_wait_for_lc_invoice = False

    @api.depends('valuation_adjustment_lines', 'valuation_adjustment_lines.invoice_id')
    def _compute_invoice_ids(self):
        for r in self:
            if r.valuation_adjustment_lines:
                r.invoice_ids = r.valuation_adjustment_lines.mapped('invoice_id')

    @api.onchange('picking_ids')
    def _onchange_picking_ids(self):
        # users may not have access right to po
        landed_cost_invoice_ids = self.picking_ids.sudo().mapped('purchase_id.landed_cost_po_ids.invoice_ids')
        for inv in landed_cost_invoice_ids:
            if inv.type not in ('in_invoice', 'in_refund'):
                continue
            self.vendor_bill_id = inv

    @api.onchange('vendor_bill_id')
    def _onchange_invoice_id(self):
        if self.vendor_bill_id:
            if self.vendor_bill_id.type not in ('in_invoice', 'in_refund'):
                raise ValidationError(_("Only Vendor Bills and Vendor Bill Credit Notes (refunds) are supported for landed costs"))

            landed_cost_inv_lines = self.vendor_bill_id.invoice_line_ids.filtered(lambda line: line.landed_cost_for_stock_done_picking_ids \
                                                                              or line.product_id.product_tmpl_id.landed_cost_ok)
            if landed_cost_inv_lines:
                self.picking_ids = landed_cost_inv_lines.mapped('landed_cost_for_stock_done_picking_ids')
            cost_lines = self.env['stock.landed.cost.lines']
            for line in landed_cost_inv_lines:
                new_line = cost_lines.new(line._prepare_landed_cost_line_data())
                cost_lines += new_line

            self.cost_lines = cost_lines


class LandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    invoice_line_id = fields.Many2one('account.move.line', string='Move Line')
    for_stock_done_picking_ids = fields.Many2many('stock.picking', string='Landed Cost for Done Pickings')


class AdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'
    
    purchase_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line', related='move_id.purchase_line_id', store=True)
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', related='purchase_line_id.order_id', store=True)
    state = fields.Selection(related='cost_id.state', store=True)
    invoice_line_id = fields.Many2one(related='cost_line_id.invoice_line_id', store=True, readonly=True, string='Landed Cost Invoice Line')
    invoice_id = fields.Many2one(related='invoice_line_id.move_id', store=True, readonly=True, string='Landed Cost Invoice')

    def _create_account_move_line(self, move, credit_account_id, debit_account_id, qty_out, already_out_account_id):
        amls = super(AdjustmentLines, self)._create_account_move_line(move, credit_account_id, debit_account_id, qty_out, already_out_account_id)
        for aml in amls:
            if self.move_id:
                aml[2]['stock_move_id'] = self.move_id.id
        return amls
