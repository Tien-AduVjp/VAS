from odoo.tests import TransactionCase


class TestCommon(TransactionCase):
    def setUp(self):
        super(TestCommon, self).setUp()

        self.product = self.env['product.product'].create({
            'name': 'Catto',
            'type': 'product',
            'uom_id': self.ref('uom.product_uom_unit'),
            'categ_id': self.ref('product.product_category_all'),
        })

        self.product_route_1 = self.env['stock.location.route'].create({
            'name': 'Input -> Stock Route',
            'product_selectable': True,
        })

        self.product_rule_1 = self.env['stock.rule'].create({
            'name': 'Input -> Stock Rule',
            'action': 'pull',
            'picking_type_id': self.ref('stock.picking_type_internal'),
            'location_src_id': self.ref('stock.stock_location_company'),
            'location_id': self.ref('stock.stock_location_stock'),
            'route_id': self.product_route_1.id,
        })

        self.warehouse_1 = self.env['stock.warehouse'].create({
            'name': 'Base Warehouse',
            'reception_steps': 'one_step',
            'delivery_steps': 'ship_only',
            'code': 'BWH'
        })

        self.location_1 = self.env['stock.location'].create({
            'name': 'TestLocation1',
            'posx': 3,
            'location_id': self.warehouse_1.lot_stock_id.id,
        })

        self.product_route_2 = self.env['stock.location.route'].create({
            'name': 'Base Warehouse -> Stock Route',
            'product_selectable': True,
            'rule_ids': [(0, 0, {
                'name': 'Base Warehouse -> Stock Rule',
                'action': 'pull',
                'picking_type_id': self.ref('stock.picking_type_internal'),
                'location_src_id': self.location_1.id,
                'location_id': self.ref('stock.stock_location_stock'),
            })],
        })

        self.approval_procurement_type = self.env['approval.request.type'].search([('type', '=', 'procurement')], limit=1)
