from odoo.tests import TransactionCase

class TestCommon(TransactionCase):
    def setUp(self):
        super(TestCommon, self).setUp()

        user_group_employee = self.ref('base.group_user')
        user_group_request_user = self.ref('to_procurement_requests.group_user')
        user_group_request_manager = self.ref('to_procurement_requests.group_manager')

        Users = self.env['res.users'].with_context({ 'no_reset_password': True })

        self.user_request_user_1 = Users.create({
            'name': 'Sarah Request User',
            'login': 'sarah_request_user',
            'email': 'sarah.request.user@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee, user_group_request_user])]
        })

        self.user_request_user_2 = Users.create({
            'name': 'John Request User',
            'login': 'john_request_user',
            'email': 'john.request.user@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee, user_group_request_user])]
        })

        self.user_request_manager_1 = Users.create({
            'name': 'Peter Request Manager',
            'login': 'peter_request_manager',
            'email': 'peter.request.manager@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee, user_group_request_manager])]
        })

        self.user_request_manager_2 = Users.create({
            'name': 'Karen Request Manager',
            'login': 'karen_request_manager',
            'email': 'karen.request.manager@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee, user_group_request_manager])]
        })

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
