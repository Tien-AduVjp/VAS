from odoo.tests import SavepointCase

class TestBase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()

        cls.partner = cls.env['res.partner'].create({'name': 'partner'})
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')

        # Setup user
        Users = cls.env['res.users'].with_context(no_reset_password=True)
        # Create a users
        cls.user_manager = Users.create({
            'name': 'Repair Manager',
            'login': 'user',
            'email': 'user2@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('to_repair_access_group.group_repair_manager').id])]
        })
        cls.product_to_repair = cls.env['product.product'].create({
            'name': 'Product To Repair',
            'type': 'product'
        })
        cls.product_consu = cls.env['product.product'].create({
            'name': 'Consumer Product',
            'type': 'consu'
        })
        cls.product_product = cls.env['product.product'].create({
            'name': 'Storable Product',
            'type': 'product'
        })
        cls.product_service1 = cls.env['product.product'].create({
            'name': 'Product Service 1',
            'type': 'service'
        })
        cls.product_service2 = cls.env['product.product'].create({
            'name': 'Product Service 2',
            'type': 'service'
        })
        cls.product_lot = cls.env['product.product'].create({
            'name': 'Product Lot',
            'type': 'product',
            'tracking': 'lot',
        })
