from odoo.tests import tagged

from .test_base import TestBase


@tagged('post_install', '-at_install')
class TestProductionLot(TestBase):

    def test_compute_repair_count_01(self):
        """
        [Functional Test] - TC02

        - Case: Check repair count of lot, which is not used in any repair order
        - Expected Result: repair count of lot is 0
        """
        self.assertTrue(self.lot2.repair_count == 0)

    def test_compute_repair_count_02(self):
        """
        [Functional Test] - TC02

        - Case: Check repair count of lot, which already used in repair orders
        - Expected Result: repair count of lot equals to number of repair orders which use it
        """
        self.assertTrue(self.lot1.repair_count == 2)
        self.assertTrue(self.lot3.repair_count == 1)
