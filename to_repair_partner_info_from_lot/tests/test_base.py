from odoo import fields
from odoo.tests import SavepointCase


class TestBase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()
        
        cls.partner_a = cls.env['res.partner'].create({'name': 'partner a'})
        cls.partner_b = cls.env['res.partner'].create({'name': 'partner b'})
        
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        
        # Create products to repair
        cls.product_to_repair = cls.env['product.product'].create({
            'name': 'Product To Repair',
            'type': 'product',
            'tracking': 'lot',
            'default_code': 'PRODUCT001'
        })
        
        # Create lots of repair products
        cls.lot1 = cls.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': cls.product_to_repair.id,
            'company_id': cls.env.company.id,
            'customer_id': cls.partner_a.id
        })
        cls.lot2 = cls.env['stock.production.lot'].create({
            'name': 'lot2',
            'product_id': cls.product_to_repair.id,
            'company_id': cls.env.company.id,
            'customer_id': cls.partner_b.id
        })
        
        # Create repair order
        cls.repair = cls.env['repair.order'].create({
            'product_id': cls.product_to_repair.id,
            'product_uom': cls.uom_unit.id,
            'address_id': cls.partner_a.id,
            'guarantee_limit': fields.Date.from_string('2022-08-31'),
            'invoice_method': 'after_repair',
            'partner_invoice_id': cls.partner_a.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
        })
        
        cls.env['stock.quant']._update_available_quantity(cls.product_to_repair, cls.env.ref('stock.stock_location_stock'), 1)
        cls.env['stock.quant']._update_available_quantity(cls.product_to_repair, cls.env.ref('stock.stock_location_stock'), 1, lot_id=cls.lot1)
