from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_landed_cost_ids = fields.Many2many('purchase.landed.cost', 'source_purchase_landed_cost_po_line_rel', 'purchase_line_id', 'purchase_landed_cost_id',
                                                string='Source Purchase Landed Costs',
                                                copy=False,
                                                help="The source purchase landed cost from which"
                                                " this order line was generated.")
    landed_cost_for_po_ids = fields.Many2many('purchase.order', string='Landed Cost for POs',
                                              compute='_compute_landed_cost_for_po_ids', store=True,
                                              copy=False,
                                              help="The source Purchase Orders that generated this order line on a separeated"
                                                        " purchase order as a landed cost")

    landed_cost_adjustment_line_ids = fields.One2many('stock.valuation.adjustment.lines', 'purchase_line_id',
                                                      string='Landed Cost Adjustment Lines')

    @api.depends('purchase_landed_cost_ids', 'purchase_landed_cost_ids.order_id')
    def _compute_landed_cost_for_po_ids(self):
        for r in self:
            po_ids = r.purchase_landed_cost_ids.mapped('order_id')
            r.landed_cost_for_po_ids = [(6, 0, po_ids.ids)]
