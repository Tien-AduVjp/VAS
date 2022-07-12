from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', related='purchase_line_id.order_id',
                                        store=True, readonly=True)
    
    landed_cost_for_po_ids = fields.Many2many('purchase.order', string='Landed Cost for POs',
                                              compute='_compute_landed_cost_for_po_ids')

    landed_cost_for_stock_picking_ids = fields.Many2many('stock.picking', string='Landed Cost for Pickings',
                                                         compute='_compute_landed_cost_for_stock_picking_ids')

    landed_cost_for_stock_done_picking_ids = fields.Many2many('stock.picking', string='Landed Cost for Done Pickings',
                                                              compute='_compute_landed_cost_for_stock_picking_ids')
    
    def _compute_landed_cost_for_po_ids(self):
        for r in self:
            r.landed_cost_for_po_ids = False
            if r.purchase_line_id.landed_cost_for_po_ids:
                r.landed_cost_for_po_ids = r.purchase_line_id.landed_cost_for_po_ids.ids

    def _compute_landed_cost_for_stock_picking_ids(self):
        for r in self:
            r.landed_cost_for_stock_done_picking_ids = False
            r.landed_cost_for_stock_picking_ids = False        
            if r.landed_cost_for_po_ids:
                picking_ids = r.landed_cost_for_po_ids.mapped('picking_ids')
                if picking_ids:
                    r.landed_cost_for_stock_picking_ids = picking_ids.ids
                    done_picking_ids = picking_ids.filtered(lambda p: p.state == 'done')
                    if done_picking_ids:
                        r.landed_cost_for_stock_done_picking_ids = done_picking_ids.ids
    
    @api.model
    def _prepare_landed_cost_line_data(self):
        #  move_lines_credit_sum and  move_lines_debit_ => 
        price_unit = 0.0
        if self.move_id.type == 'in_invoice':
            price_unit = self.debit
        elif self.move_id.type == 'in_refund':
            price_unit = self.credit
        else:
            raise ValidationError(_("Only Vendor Bills and Vendor Bill Credit Notes (refunds) are supported for landed costs"))
        
        data = {
            'name': self.product_id.name or '',
            'invoice_line_id': self.id,
            'product_id': self.product_id.id,
            'split_method': 'equal',
            'account_id': self.product_id.product_tmpl_id._get_product_accounts()['expense'],
            'price_unit': price_unit,
            }
        if self.landed_cost_for_stock_done_picking_ids:
            data['for_stock_done_picking_ids'] = [(6, 0, self.landed_cost_for_stock_done_picking_ids.ids)]
        return data

