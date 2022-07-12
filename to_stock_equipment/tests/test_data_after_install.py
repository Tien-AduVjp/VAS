from odoo.tests import tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestData(Common):

    def test_data_after_install(self):
        # Check the data of the receipt operation type
        operation_receipt = self.StockPickingType.search([('code', '=', 'incoming')])
        self.assertTrue(any(operation_receipt.mapped('can_create_equipment')))
