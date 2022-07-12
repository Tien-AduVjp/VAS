from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestHrEmployeeSkillReport(Common):
    def setUp(self):
        super(Common, self).setUp()
        # company
        self.company_2 = self.env['res.company'].create({'name': 'Company 2'})
        self.department_technical = self.env['hr.department'].with_company(self.company_2).create({
            'name' : 'Department Technical'
        })
        self.department_hr = self.env['hr.department'].with_company(self.company_2).create({
            'name' : 'Department Human Resource'
        })
        # job
        self.job_dev = self.env['hr.job'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'name' : 'Job Dev'
            })
        # user
        self.user_hr_skill1 = self.env['res.users'].with_context({
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).with_company(self.company_2).create({
                'name': 'User skill 1',
                'login': 'employee_hr_skill1',
                'email': 'employee_hr_skill1@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        self.user_hr_officer1 = self.env['res.users'].with_context({
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).with_company(self.company_2).create({
                'name': 'HR Officer1',
                'login': 'hr_officer1',
                'email': 'hr_officer1@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('hr.group_hr_user').id])],
        })
        self.user_skill_officer1 = self.env['res.users'].with_context({
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).with_company(self.company_2).create({
                'name': 'Skill Officer1',
                'login': 'skill_officer1',
                'email': 'skill_officer1@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('viin_hr_skill_framework.group_skill_officer').id])],
        })
        # role
        self.role_mobile_developer =  self.env['hr.role'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'name': 'Role Mobile Developer',
            'department_id' : self.department_technical.id
            })
        self.role_hr = self.env['hr.role'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'name': 'Role Hr',
            'department_id' : self.department_hr.id
            })
        # grade
        self.grade_senior_1 = self.env['hr.employee.grade'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'name': 'Senior 1'
            })
        self.grade_junior_1 = self.env['hr.employee.grade'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'name': 'Junior 1',
            'parent_id' : self.grade_senior_1.id
            })
        # rank
        self.rank_mobile_developer_senior = self.env['hr.rank'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'role_id' : self.role_mobile_developer.id,
            'grade_id' : self.grade_senior_1.id
            })
        self.rank_mobile_developer_junior = self.env['hr.rank'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'role_id' : self.role_mobile_developer.id,
            'grade_id' : self.grade_junior_1.id,
            'parent_id' : self.rank_mobile_developer_senior.id
            })
        self.rank_hr_junior = self.env['hr.rank'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'role_id' : self.role_hr.id,
            'grade_id' : self.grade_junior_1.id
            })
        # skill type
        self.skill_type_dev = self.env['hr.skill.type'].with_context(tracking_disable=True).create({
            'name' : 'Developer',
            })
        self.skill_type_hr = self.env['hr.skill.type'].with_context(tracking_disable=True).create({
            'name' : 'Human resource'
            })
        # skill level
        self.level_beginner_dev = self.env['hr.skill.level'].with_context(tracking_disable=True).create({
            'name' : 'Beginner',
            'level_progress' : 25,
            'skill_type_id' : self.skill_type_dev.id
            })
        self.level_intermediate_dev = self.env['hr.skill.level'].with_context(tracking_disable=True).create({
            'name' : 'Intermediate',
            'level_progress' : 50,
            'skill_type_id' : self.skill_type_dev.id
            })
        self.level_expert_dev = self.env['hr.skill.level'].with_context(tracking_disable=True).create({
            'name' : 'Expert',
            'level_progress' : 100,
            'skill_type_id' : self.skill_type_dev.id
            })
        self.level_beginner_hr = self.env['hr.skill.level'].with_context(tracking_disable=True).create({
            'name' : 'Beginner',
            'level_progress' : 25,
            'skill_type_id' : self.skill_type_hr.id
            })
        self.level_intermediate_hr = self.env['hr.skill.level'].with_context(tracking_disable=True).create({
            'name' : 'Intermediate',
            'level_progress' : 50,
            'skill_type_id' : self.skill_type_hr.id
            })
        self.level_expert_hr = self.env['hr.skill.level'].with_context(tracking_disable=True).create({
            'name' : 'Expert',
            'level_progress' : 100,
            'skill_type_id' : self.skill_type_hr.id
            })
        # Skills
        self.skill_viindoo = self.env['hr.skill'].with_context(tracking_disable=True).create({
            'name' : 'Viindoo Framework',
            'skill_type_id': self.skill_type_dev.id
            })
        self.skill_communication = self.env['hr.skill'].with_context(tracking_disable=True).create({
            'name' : 'Communication',
            'skill_type_id': self.skill_type_hr.id
            })
        # create employee
        self.user_hr_skill1.action_create_employee()
        self.user_skill_officer1.action_create_employee()
        self.user_hr_officer1.action_create_employee()
        self.employee_hr_skill1 = self.user_hr_skill1.employee_id
        self.skill_officer1 = self.user_skill_officer1.employee_id
        self.hr_officer1 = self.user_hr_officer1.employee_id
        # set department
        self.employee_hr_skill1.department_id = self.department_technical
        self.skill_officer1.department_id = self.department_technical
        self.department_technical.manager_id = self.skill_officer1
        self.hr_officer1.department_id = self.department_hr.id
        # set rank
        self.skill_officer1.rank_id = self.rank_mobile_developer_junior
        self.employee_hr_skill1.rank_id = self.rank_mobile_developer_junior
        self.hr_officer1.rank_id = self.rank_hr_junior
        # Employee's skill
        self.employee_skill = self.env['hr.employee.skill'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'employee_id' : self.employee_hr_skill1.id,
            'skill_id' : self.skill_viindoo.id,
            'skill_level_id' : self.level_beginner_dev.id,
            'skill_type_id' : self.skill_type_dev.id,
            })
        self.skill_officer_skill = self.env['hr.employee.skill'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'employee_id' : self.skill_officer1.id,
            'skill_id' : self.skill_viindoo.id,
            'skill_level_id' : self.level_beginner_dev.id,
            'skill_type_id' : self.skill_type_dev.id,
            })
        self.hr_officer_skill = self.env['hr.employee.skill'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'employee_id' : self.hr_officer1.id,
            'skill_id' : self.skill_communication.id,
            'skill_level_id' : self.level_beginner_hr.id,
            'skill_type_id' : self.skill_type_hr.id,
            })
        # Skill description
        self.skill_viindoo_begin_description = self.env['hr.skill.description'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'skill_type_id' : self.skill_type_dev.id,
            'skill_id': self.skill_viindoo.id,
            'skill_level_id': self.level_beginner_dev.id
            })
        self.skill_viindoo_intermediate_description = self.env['hr.skill.description'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'skill_type_id' : self.skill_type_dev.id,
            'skill_id': self.skill_viindoo.id,
            'skill_level_id': self.level_intermediate_dev.id
            })
        self.skill_communication_begin_description = self.env['hr.skill.description'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'skill_type_id' : self.skill_type_hr.id,
            'skill_id': self.skill_communication.id,
            'skill_level_id': self.level_beginner_hr.id
            })
        # Add skill to rank
        self.rank_mobile_developer_junior_skill_description = self.env['hr.rank.skill.description'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'rank_id' : self.rank_mobile_developer_junior.id,
            'skill_type_id' : self.skill_type_dev.id,
            'skill_id': self.skill_viindoo.id,
            'skill_level_id': self.level_beginner_dev.id,
            'expectation' : 'required'
            })
        self.rank_mobile_developer_senior_skill_description = self.env['hr.rank.skill.description'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'rank_id' : self.rank_mobile_developer_senior.id,
            'skill_type_id' : self.skill_type_dev.id,
            'skill_id': self.skill_viindoo.id,
            'skill_level_id': self.level_intermediate_dev.id,
            'expectation' : 'required'
            })
        self.rank_hr_junior_description = self.env['hr.rank.skill.description'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'rank_id' : self.rank_hr_junior.id,
            'skill_type_id' : self.skill_type_hr.id,
            'skill_id' : self.skill_communication.id,
            'skill_level_id': self.level_beginner_hr.id,
            'expectation' : 'required'
            })
        self.rank_mobile_developer_junior.flush()

    def test_access_right_report_1(self):
        """
        Internal User only see their own personal report
        """
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        self.assertEqual(self.report_demo.mapped('employee_id'), self.employee_hr_skill1)
        with self.assertRaises(AccessError):
            self.report_demo.with_user(self.user_hr_skill1).unlink()
        with self.assertRaises(AccessError):
            self.report_demo.with_user(self.user_hr_skill1).write({
                'reach_progress' : 50
                })

    def test_access_right_report_2(self):
        """
        User Skill Officer able to see their own report
        and from their subordinates
        """
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_skill_officer1).search([])
        # user_skill_officer1 is able to see 2 report
        # - Their own report
        # - Their subordinates: user_hr_skill1
        self.assertEqual(self.report_demo.mapped('employee_id'), self.employee_hr_skill1 | self.skill_officer1)
        with self.assertRaises(AccessError):
            self.report_demo.with_user(self.user_skill_officer1).unlink()
        with self.assertRaises(AccessError):
            self.report_demo.with_user(self.user_skill_officer1).write({
                'reach_progress' : 50
                })

    def test_access_right_report_3(self):
        """
        User Hr Officer able to see all report
        """
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_officer1).search([('company_id','=',self.company_2.id)])
        # Hr Officer will able to see all report from company_2: user_skill_officer1, user_hr_skill1
        self.assertEqual(self.report_demo.mapped('employee_id'), self.employee_hr_skill1 | self.skill_officer1 | self.hr_officer1)
        with self.assertRaises(AccessError):
            self.report_demo.with_user(self.user_hr_officer1).unlink()
        with self.assertRaises(AccessError):
            self.report_demo.with_user(self.user_hr_officer1).write({
                'reach_progress' : 50
                })

    def test_report_skill_framework_1(self):
        """
        Input: Employee's rank is null
        Expected: Skill framework report for this employee will not be executed
        """
        self.employee_hr_skill1.grade_id = False
        self.employee_hr_skill1.role_id = False
        self.rank_mobile_developer_junior.flush()
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        self.assertEqual(len(self.report_demo), 0, "Report for this user should not be executed")

    def test_report_skill_framework_2(self):
        """
        Employee's rank have been set value
        Expected: Report display information corresponding to employee
        """
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        employeeID = self.report_demo.mapped('employee_id')
        self.assertEqual(employeeID, self.employee_hr_skill1)
        self.assertEqual(employeeID.department_id, self.employee_hr_skill1.department_id)
        self.assertEqual(employeeID.rank_id, self.employee_hr_skill1.rank_id)
        self.assertEqual(employeeID.next_rank_id, self.employee_hr_skill1.next_rank_id)
        self.assertEqual(employeeID.employee_skill_ids, self.employee_skill)

    def test_report_skill_framework_3(self):
        """
        Employee's current rank requires skill that employee don't have
        Expected: reach_progress equals to 0
        """
        self.employee_hr_skill1.employee_skill_ids = False
        self.rank_mobile_developer_junior.flush()
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        self.assertEqual(self.report_demo.reach_progress, 0, "Current Rank Reach Progress should be zero")

    def test_report_skill_framework_4(self):
        """
        Employee's current rank requires skill that employee don't have
        Employee's next rank also requires skill that employee don't have
        Expected: reach_progress and next_rank_reach_progress equal to 0
        """
        self.employee_hr_skill1.employee_skill_ids = False
        self.rank_mobile_developer_junior.flush()
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        self.assertEqual(self.report_demo.reach_progress, 0, "Current Rank Reach Progress should be zero")
        self.assertEqual(self.report_demo.next_rank_reach_progress, 0, "Next Rank Reach Progress should be zero")

    def test_report_skill_framework_5(self):
        """
        Employee's skill not belong to Employee's rank
        Expected: That skills will not show up on report
        """
        self.employee_skill_2 = self.env['hr.employee.skill'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'employee_id' : self.employee_hr_skill1.id,
            'skill_id' : self.skill_communication.id,
            'skill_level_id' : self.level_beginner_hr.id,
            'skill_type_id' : self.skill_type_hr.id,
            })
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        self.assertFalse(self.employee_skill_2.skill_id in self.report_demo.mapped('skill_id'), "This skill should not show up on report")

    def test_report_skill_framework_6(self):
        """
        Employee's skill meet current rank's skill
        Expected: reach_progress will compute by formula current_level/required_level * 100
        """
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        #current rank's skill: [viindoo-beginner level] - level progress: 25
        #employee skill: [viindoo-beginner level] - level progress: 25
        self.assertEqual(self.report_demo.reach_progress, 100)

    def test_report_skill_framework_7(self):
        """
        Employee's skill meet current rank's skill but not meet next rank's skill
        Expected:
            reach_progress will compute by formula current_level/required_level * 100
            next_rank_reach_progress will compute by formula current_level/next_rank_level_required * 100

        """
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        #current rank's skill: [viindoo - beginner level] - level progress: 25
        #next rank's skill: [viindoo - intermediate level] - level progress: 50
        #employee skill: [viindoo - beginner level] - level progress: 25
        self.assertEqual(self.report_demo.reach_progress, 100)
        self.assertEqual(self.report_demo.next_rank_reach_progress, 50)

    def test_report_skill_framework_8(self):
        """
        Employee's skill meet current rank's skill also meet next rank's skill
        Expected:
            reach_progress will compute by formula current_level/required_level * 100
            next_rank_reach_progress will compute by formula current_level/next_rank_level_required * 100

        """
        self.employee_skill.write({
            'skill_level_id' : self.level_intermediate_dev.id
            })
        self.rank_mobile_developer_junior.flush()
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        #current rank's skill: [viindoo - beginner level] - level progress: 25
        #next rank's skill: [viindoo - intermediate level] - level progress: 50
        #employee skill: [viindoo - intermediate level] - level progress: 50
        self.assertEqual(self.report_demo.reach_progress, 100)
        self.assertEqual(self.report_demo.next_rank_reach_progress, 100)

    def test_report_skill_framework_9(self):
        """
        Next rank required skills are different from the current rank
        Expected: Report will show up the skill that don't have in current rank
        """
        self.rank_mobile_developer_senior_skill_description_2 = self.env['hr.rank.skill.description'].with_context(tracking_disable=True).with_company(self.company_2).create({
            'rank_id' : self.rank_mobile_developer_senior.id,
            'skill_type_id' : self.skill_type_hr.id,
            'skill_id': self.skill_communication.id,
            'skill_level_id': self.level_beginner_hr.id,
            'expectation' : 'required'
            })
        self.rank_mobile_developer_junior.flush()
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        self.assertTrue(self.rank_mobile_developer_senior_skill_description_2.skill_level_id in self.report_demo.mapped('next_rank_skill_level_id'))

    def test_report_skill_framework_10(self):
        """
        Employee has highest rank
        Expected: The next rank of employee is current rank of this employee
        """
        self.employee_hr_skill1.rank_id = self.rank_mobile_developer_senior
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        self.assertEqual(self.report_demo.mapped('next_rank_id'), self.employee_hr_skill1.rank_id)

    def test_report_skill_framework_11(self):
        """
        Change employee skill level
        Expected: Report will recalculate reach progress
        """
        self.employee_skill.write({
            'skill_level_id' : self.level_expert_dev.id
            })
        self.rank_mobile_developer_junior.flush()
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        # Employee level : 100
        # Current rank level : 25
        # Next rank level: 50
        self.assertEqual(self.report_demo.reach_progress, 100.0)
        self.assertEqual(self.report_demo.next_rank_reach_progress, 100.0)

    def test_report_skill_framework_12(self):
        """
        Remove the next rank
        Expected: Rank parent-child chains and reports will be recomputed
        """
        # Current rank chains:
        # [Junior] mobile dev -> [Senior] mobile dev
        self.rank_mobile_developer_senior.unlink()
        self.rank_mobile_developer_junior.flush()
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.user_hr_skill1).search([])
        self.assertEqual(self.report_demo.mapped('next_rank_id'), self.employee_hr_skill1.rank_id)
