from odoo import models, fields


class ProductSet(models.Model):
    _name = 'product.set'
    _description = 'Product Set'
    _order = 'sequence'
    """ Model nay duoc thiet ke de luu du lieu tam thoi cua thiet bi dong bo duoc tao boi san pham co
    thiet lap bomkit tren don hang mua. Du lieu tu model nay se duoc su dung khi can tao thiet bi cho
    san pham dong bo chua cac thiet bi con se duoc nhan ve trong picking nay.
    """

    name = fields.Char(string='Ref', readonly=True)
    sequence = fields.Integer(default=1)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_qty = fields.Float(string='Quantity', readonly=True)
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure', readonly=True)
    can_create_equipment = fields.Boolean(string='Create Equipment')
    picking_id = fields.Many2one('stock.picking', string='Stock Picking')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    bom_id = fields.Many2one('mrp.bom', string='Bom Kit', readonly=True)
    purchase_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line')
    line_ids = fields.One2many('product.set.line', 'product_set_id', string='Product Set Line', readonly=True)

class ProductSetLine(models.Model):
    _name = 'product.set.line'
    _description = 'Product Set Line'
    """Model nay luu thong tin cac thiet bi con co the duoc tao tu thiet bi cha tren, duoc sinh ra dua
    tren bom_id, so luong remaining_id se tru dan di cho den khi nhan du cac thiet bi con.
    """

    product_set_id = fields.Many2one('product.set', string='Product Set', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Quantity')
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    remaining_qty = fields.Float(string='Remaining Quantity')
