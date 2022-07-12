from odoo import models, fields, api, _


class PurchaseLandedCost(models.Model):
    _name = 'purchase.landed.cost'
    _description = 'Purchasse Landed Cost'
    _rec_name = 'product_id'

    order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)

    product_id = fields.Many2one('product.product', string='Landed Cost Product', required=True, ondelete='cascade', index=True,
                                 help="The product that present this landed cost. For example, transportation fee, stowage fee, etc")

    product_uom_qty = fields.Float(string='Quantity', default=1.0, required=True)
    product_uom_category_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True,
                                  domain="[('category_id', '=', product_uom_category_id)]")

    date_order = fields.Datetime(string='Scheduled Order Date', compute='_get_date_order', inverse='_set_date_order', store=True,
                                 help="The date on which you will order this landed cost")
    picking_type_id = fields.Many2one(related='order_id.picking_type_id', store=True)

    @api.model
    def get_seller(self):
        return self.product_id._select_seller(
            partner_id=False,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom_id)

    @api.model
    def _prepare_po_line_data(self):
        name = _("Landed cost for %s") % (self.order_id.name,)
        if self.product_id.description_purchase:
            name = '%s\n%s' % (self.product_id.description_purchase, name)

        return {
            'product_id': self.product_id.id,
            'date_planned': self.date_order,
            'product_qty': self.product_uom_qty,
            'product_uom': self.product_uom_id,
            'name': name,
            'purchase_landed_cost_ids':[(4, self.id)]
            }

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id.uom_po_id:
            self.product_uom_id = self.product_id.uom_po_id
        else:
            self.product_uom_id = self.product_id.uom_id

    @api.depends('order_id', 'order_id.date_order')
    def _get_date_order(self):
        for r in self:
            r.date_order = r.order_id.date_order

    def _set_date_order(self):
        pass

