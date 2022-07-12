from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestLocationWarehouse(TransactionCase):

    def setUp(self):
        super(TestLocationWarehouse, self).setUp()

        self.warehouse1 = self.env['stock.warehouse'].create({
            'name':'AAA',
            'code':'a',
        })
        self.location_view1 = self.warehouse1.view_location_id
        self.warehouse2 = self.env['stock.warehouse'].create({
            'name':'BBB',
            'code':'b',
        })
        self.location_view2 = self.warehouse2.view_location_id

        self.location = self.env['stock.location'].create({
            'name':'Location',
            'location_id': self.location_view1.id
        })
        self.location2 = self.env['stock.location'].create({
            'name':'Location2',
            'location_id':self.location.id
        })

    def test_compute_warehouse(self):
        self.assertEqual(self.location.warehouse_id, self.warehouse1, 'Warehouse is incorrect!')
        self.location.write({'location_id':self.location_view2.id})
        self.assertEqual(self.location.warehouse_id, self.warehouse2, 'Warehouse is incorrect!')
        self.location.write({'location_id':False})
        self.assertEqual(bool(self.location.warehouse_id), False, 'Warehouse is incorrect!')

    def test_get_sublocations(self):
        self.stock_default_view = self.location_view1.child_ids.filtered(lambda r: r.name == 'Stock')
        sublocations = self.env['stock.location'].browse([self.location_view1.id, self.location.id, self.location2.id, self.stock_default_view.id])
        self.assertEqual(self.location_view1.get_sublocations(), sublocations, 'Sublocations is incorrect!')

    def test_constrains_check_view_location_id(self):
        with self.assertRaises(ValidationError):
            self.warehouse2.write({'view_location_id':self.location_view1.id})
