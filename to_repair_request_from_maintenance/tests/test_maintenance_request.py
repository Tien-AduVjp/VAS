from odoo import fields
from odoo.tests import tagged

from .test_common import TestCommon

@tagged('post_install', '-at_install')
class TestMaintenanceRequest(TestCommon):

    def test_compute_repair_count_01(self):
        """
        [Functional Test] - TC01

        - Case: Check repair count of maintenance request in case there is no repair order related to a maintenance request
        - Expected Result: Repair count of maintenance request is 0
        """
        self.assertTrue(self.maintenance_request1.repair_count == 0)


    def test_compute_repair_count_02(self):
        """
        [Functional Test] - TC02

        - Case: Check repair count of maintenance request in case there are 2 repair order related to a maintenance request
        - Expected Result: Repair count of maintenance request is 2
        """
        # Create repair order
        self.env['repair.order'].create({
            'product_id': self.product_to_repair1.id,
            'product_uom': self.uom_unit.id,
            'address_id': self.partner_a.id,
            'guarantee_limit': fields.Date.from_string('2022-08-27'),
            'invoice_method': 'b4repair',
            'partner_invoice_id': self.partner_a.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'partner_id': self.partner_a.id,
            'maintenance_request_id': self.maintenance_request1.id,
            'lot_id': self.lot1.id
        })

        self.env['repair.order'].create({
            'product_id': self.product_to_repair1.id,
            'product_uom': self.uom_unit.id,
            'address_id': self.partner_a.id,
            'guarantee_limit': fields.Date.from_string('2022-08-27'),
            'invoice_method': 'b4repair',
            'partner_invoice_id': self.partner_a.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'partner_id': self.partner_a.id,
            'maintenance_request_id': self.maintenance_request1.id,
            'lot_id': self.lot1.id
        })

        self.assertTrue(self.maintenance_request1.repair_count == 2)
