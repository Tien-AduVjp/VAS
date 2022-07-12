from odoo import api, fields, models


class MrpEcoBomChange(models.Model):
    _name = 'mrp.eco.bom.change'
    _description = 'ECO Material Changes'

    eco_id = fields.Many2one('mrp.eco', string='Engineering Change', ondelete='cascade', required=True)
    change_type = fields.Selection([
        ('add', 'Add'),
        ('remove', 'Remove'),
        ('update', 'Update')], string='Type', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom_id = fields.Many2one('uom.uom', string='Product  UoM', required=True)
    old_product_qty = fields.Float(string='Previous Revision Quantity', default=0)
    new_product_qty = fields.Float(string='New Revision Quantity', default=0)
    upd_product_qty = fields.Float(string='Quantity', compute='_compute_upd_product_qty', store=True)

    @api.depends('new_product_qty', 'old_product_qty')
    def _compute_upd_product_qty(self):
        for r in self:
            r.upd_product_qty = r.new_product_qty - r.old_product_qty
