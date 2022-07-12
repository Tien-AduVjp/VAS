from odoo.tests.common import tagged, Form
from .common import Common


@tagged('-at_install', 'post_install')
class QualityForm(Common):

    def test_01_validate_team(self):
        """
        Case 1: Authentication when creating quality check select quality point, then automatically select quality control team
        """
        self.quality_check = Form(self.env['quality.check'])
        self.quality_check.point_id = self.quality_point_pass_fail
        self.assertEqual(self.quality_check.team_id, self.quality_point_pass_fail.team_id)

    def test_quality_check_user_id(self):
        """ Quality point is assigned to a specific user, check created from that point will be assigned to the same user """
        self.quality_point_pass_fail.user_id = self.internal_user
        quality_check_form = Form(self.env['quality.check'])
        quality_check_form.point_id = self.quality_point_pass_fail
        self.assertEqual(quality_check_form.user_id, self.internal_user)
        quality_check = quality_check_form.save()
        self.assertEqual(quality_check.user_id, self.internal_user)

    def test_11_check_tolerance_max(self):
        """
        Case 2: The default max tolerance will take the norm
        """
        point_form = Form(self.env['quality.point'])
        point_form.test_type_id = self.measure_type
        point_form.norm = 50
        self.assertEqual(point_form.tolerance_max, 50)
