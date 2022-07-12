from odoo.tests import tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestEquipment(Common):

    def test_check_compute_equipment(self):
        # Create a manual equipment
        equipment = self.Equipment.create({
            'name': 'Equipment Demo',
            'lot_id': self.lot1.id
        })
        self.assertIn(equipment.id, self.Equipment.search([]).ids)
        self.assertEqual(equipment.lot_id.id, self.lot1.id)
        self.assertEqual(equipment.product_id.id, self.lot1.product_id.id)
        self.assertEqual(equipment.serial_no, self.lot1.name)

        # Write lot_id of equipment
        equipment.write({'lot_id': self.lot2.id})
        self.assertEqual(equipment.lot_id.id, self.lot2.id)
        self.assertEqual(equipment.product_id.id, self.lot2.product_id.id)
        self.assertNotEqual(equipment.serial_no, self.lot2.name)
