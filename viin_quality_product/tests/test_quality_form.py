from odoo.tests.common import tagged, Form
from .common import Common


@tagged('-at_install', 'post_install')
class QualityForm(Common):

    def test_01_validate_product(self):
        """
        Case 1: Authentication when creating quality check select quality point, then automatically select quality control team
        """
        self.quality_check = Form(self.env['quality.check'])
        self.quality_check.point_id = self.quality_point_pass_fail_2
        self.assertEqual(self.quality_check.product_id, self.quality_point_pass_fail_2.product_id)
