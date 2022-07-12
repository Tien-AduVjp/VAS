from odoo.tests import tagged

from odoo.addons.repair.tests.test_repair import TestRepair

@tagged('post_install', '-at_install')
class TestRepairOfOdoo(TestRepair):

    def setUp(self):
        super(TestRepairOfOdoo, self).setUp()
        self.env['stock.quant']._update_available_quantity(self.env.ref('product.product_product_5'),
                                                           self.env.ref('stock.stock_location_stock').sudo(), 2.0)
