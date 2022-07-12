from odoo.tests.common import SavepointCase, Form


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.Equipment = cls.env['maintenance.equipment']
        cls.Product = cls.env['product.product'].with_context(default_can_be_equipment=True)
        cls.StockPicking = cls.env['stock.picking']
        cls.StockPickingType = cls.env['stock.picking.type']
        cls.StockMove = cls.env['stock.move']
        cls.StockMoveLine = cls.env['stock.move.line']
        cls.product_form = Form(cls.Product)
        cls.product_form.name = 'Product Equipment'
        cls.product = cls.product_form.save()
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.company_location = cls.env.ref('stock.stock_location_stock')
        cls.picking_type_in = cls.env.ref('stock.picking_type_in')
        cls.lot1 = cls.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': cls.product.id,
            'company_id': cls.env.company.id,
        })
        
        cls.lot2 = cls.env['stock.production.lot'].create({
            'name': 'lot2',
            'product_id': cls.product.id,
            'company_id': cls.env.company.id,
        })
        
        cls.picking = cls.env['stock.picking'].create({
            'picking_type_id': cls.picking_type_in.id,
            'location_id' : cls.supplier_location.id,
            'location_dest_id': cls.company_location.id,
        })
        
        cls.move_line_1 = cls.env['stock.move.line'].create({
            'product_id': cls.product.id,
            'qty_done': 1,
            'product_uom_id': cls.product.uom_id.id,
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.company_location.id,
            'lot_name': 'lot01',
            'can_create_equipment': True,
            'picking_id': cls.picking.id,
        })
        
        cls.move_line_2 = cls.env['stock.move.line'].create({
            'product_id': cls.product.id,
            'qty_done': 1,
            'product_uom_id': cls.product.uom_id.id,
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.company_location.id,
            'lot_name': 'lot02',
            'can_create_equipment': True,
            'picking_id': cls.picking.id,
        })
