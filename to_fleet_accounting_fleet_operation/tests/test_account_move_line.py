from odoo.tests.common import tagged
from .common import FleetAccountingFleetOperationCommon


@tagged('post_install', '-at_install')
class TestFletAccountMoveLine(FleetAccountingFleetOperationCommon):

    def test_04_account_move_line(self):
        self.assertTrue(self.invoice.invoice_line_ids[0].trip_id, "")
