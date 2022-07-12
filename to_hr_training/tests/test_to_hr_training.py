from odoo.tests import tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestToHrTraining(Common):

    def test_compute_course_1(self):
        """
        Adding course to skill type, skill, skill level
        Expect: counting course in Current Rank, Next Rank, Employee
        """
        #compute course for current rank
        self.assertEqual(self.employee.employee_id.slide_channel_for_current_rank_ids, self.course_1)
        #compute course for next rank
        self.assertEqual(self.employee.employee_id.slide_channel_for_next_targeted_rank_ids, self.course_2)
