from odoo.tests import tagged

from .test_activity_planning_common import TestActivityPlanningCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestActivityPlanningFunction(TestActivityPlanningCommon):

    def test_01_message_follower(self):
        self.assertEqual(self.richard_emp.message_follower_ids,
                         self.richard_emp_public.message_follower_ids,
                         "Followers in the Public employee are not the same in the Employee"
                         )

    # Compare employee activity created with plan
    def test_02_activity_and_message_on_employee(self):
        employee_activity_summaries = self.richard_emp.activity_ids.mapped('summary')
        employee_activity_type_ids = self.richard_emp.activity_ids.activity_type_id.ids
        responsible_activities = self.richard_emp.activity_ids.user_id.ids

        for activity_type in self.onboarding_plan.plan_activity_type_ids:
            # Check activity summary
            self.assertIn(activity_type.summary, employee_activity_summaries)
            # Check activity type
            self.assertIn(activity_type.activity_type_id.id, employee_activity_type_ids)
            # Check responsible
            responsible = activity_type.get_responsible_id(self.richard_emp)
            self.assertIn(responsible.id, responsible_activities)

    # Compare employee private activity with employee public activity
    def test_03_activity_and_message_on_employee_public(self):
        richard_emp_public_activities = self.richard_emp_public.with_user(self.richard).activity_ids
        self.assertGreater(len(richard_emp_public_activities), 0)

    # Check activities of manager
    def test_04_activities_and_message_on_employee_public_of_manager(self):
        richard_emp_public_activities = self.richard_emp_public.with_user(self.hubert).activity_ids
        self.assertGreater(len(richard_emp_public_activities), 1)

    # Compare employee private message with employee public message when click Done activity
    def test_05_activity_done(self):
        activity_to_check = self.richard_emp_public.with_user(self.richard).activity_ids[0]
        self.richard_emp_public.with_user(self.richard).activity_ids[0]._action_done()
        self.assertNotIn(activity_to_check, self.richard_emp_public.with_user(self.richard).activity_ids)
