from odoo.exceptions import AccessError

from odoo.tests import tagged

from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestHrOvertimeAccessRight(Common):

    def test_01_access_right_ot_rule_base_user(self):
        """
            Case: Test access right overtime rule of base user.
            Expect: Base user can readonly.
        """
        with self.assertRaises(AccessError):
            self.env['hr.overtime.rule'].with_user(self.user_01).create({
                'name':'Friday Daytime Extra',
                'hour_from': 12.0,
                'hour_to': 18.0,
                'weekday': '4',
                'code_id':self.env.ref('viin_hr_overtime.rule_code_ot0618').id
                })

        with self.assertRaises(AccessError):
            self.monday_evening_ot_rule.with_user(self.user_01).write({
                'hour_to': 16.0
            })
        with self.assertRaises(AccessError):
            self.monday_evening_ot_rule.with_user(self.user_01).unlink()
        self.assertTrue(self.monday_evening_ot_rule.with_user(self.user_01).read())

    def test_02_access_right_ot_rule_manager(self):
        """
            Case: Test access right for overtime rule of manager.
            Expect: Manager should have full access right (read/write/create/unlink)
        """
        self.user_01.groups_id = [(4, self.env.ref('viin_hr_overtime.group_overtime_admin').id, 0)]
        self.friday_day_ot_rule = self.env['hr.overtime.rule'].search(
            [('weekday', '=', '4'),
            ('code', '=', self.env.ref('viin_hr_overtime.rule_code_ot0618').name),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        self.friday_day_ot_rule.hour_to = 12.0
        friday_datetime_extra = self.env['hr.overtime.rule'].with_user(self.user_01).create({
            'name':'Friday Daytime Extra',
            'hour_from': 12.0,
            'hour_to': 18.0,
            'weekday': '4',
            'code_id': self.env.ref('viin_hr_overtime.rule_code_ot0618').id
        })
        self.assertTrue(friday_datetime_extra and True)
        is_write_overtime_rule = friday_datetime_extra.with_user(self.user_01).write({
            'name':'Friday Datetime Extra Edit',
            'hour_to':16.0
        })
        self.assertTrue(is_write_overtime_rule)
        self.assertTrue(friday_datetime_extra.with_user(self.user_01).unlink())
        self.assertTrue(self.monday_evening_ot_rule.with_user(self.user_01).read())

    def test_03_access_right_ot_reason_base_user(self):
        """
            Case: Test access right overtime reason of base user.
            Expect: Base User have readonly access right.
        """
        with self.assertRaises(AccessError):
            self.env['hr.overtime.reason'].with_user(self.user_01).create({
                'name':'OT by new project.'
            })
        with self.assertRaises(AccessError):
            self.overtime_reason_general.with_user(self.user_01).write({
                'name': 'New Reason for testing'
            })
        with self.assertRaises(AccessError):
            self.overtime_reason_general.with_user(self.user_01).unlink()
        self.assertTrue(self.overtime_reason_general.with_user(self.user_01).read())

    def test_04_access_right_ot_reason_manager(self):
        """
            Case: Test access right overtime reason of manager.
            Expect: Manager should have full access right (read/write/create/unlink).
        """
        self.user_01.groups_id = [(4, self.env.ref('viin_hr_overtime.group_overtime_admin').id, 0)]
        ot_reason = self.env['hr.overtime.reason'].with_user(self.user_01).create({
            'name':'OT by new project'
        })
        self.assertTrue(ot_reason and True)
        self.assertTrue(self.overtime_reason_general.with_user(self.user_01).read())
        is_write_ot_reason = self.overtime_reason_general.with_user(self.user_01).write({
            'name':'New Reason for testing'
        })
        self.assertRaises(is_write_ot_reason)
        self.assertTrue(self.overtime_reason_general.with_user(self.user_01).unlink())

    def test_05_access_right_ot_rule_code_base_user(self):
        """
            Case: Test access right overtime rule code of base user.
            Expect: Base user should have readonly access right.
        """
        with self.assertRaises(AccessError):
            self.env['hr.overtime.rule.code'].with_user(self.user_01).create({
                'name':'OT0024',
                'pay_rate':400.0
            })

        with self.assertRaises(AccessError):
            self.env.ref('viin_hr_overtime.rule_code_ot0006').with_user(self.user_01).write({
                'pay_rate':400.0
            })
        with self.assertRaises(AccessError):
            self.env.ref('viin_hr_overtime.rule_code_ot0006').with_user(self.user_01).unlink()
        self.assertTrue(self.env.ref('viin_hr_overtime.rule_code_ot0006').with_user(self.user_01).read())

    def test_06_access_right_ot_rule_code_manager(self):
        """
            Case: Test access right overtime rule code of manager.
            Expect: Manager should have full access right (read/write/create/unlink).
        """
        self.user_01.groups_id = [(4, self.env.ref('viin_hr_overtime.group_overtime_admin').id, 0)]
        ot_rule_code = self.env['hr.overtime.rule.code'].with_user(self.user_01).create({
            'name':'OTEX0006',
            'pay_rate':180.0
        })
        self.assertTrue(ot_rule_code and True)
        self.assertTrue(self.env.ref('viin_hr_overtime.rule_code_ot0006').with_user(self.user_01).read())
        is_write_ot_rule_code = self.env.ref('viin_hr_overtime.rule_code_ot0006').with_user(self.user_01).write({
            'name':'OTEX006'
        })
        self.assertTrue(is_write_ot_rule_code)
        self.assertTrue(ot_rule_code.with_user(self.user_01).unlink())

    def test_07_access_right_ot_plan_base_user(self):
        """
            Case: Test access right overtime plan of base user.
            Expect: Base user have full access right (read/write/create/unlink) to their plan,
                    but cannot access to other users plan.
        """
        is_write_ot_plan = self.overtime_plan_emp_01.with_user(self.user_01).write({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
        })
        self.assertTrue(is_write_ot_plan)
        with self.assertRaises(AccessError):
            self.overtime_plan_emp_01.with_user(self.user_02).write({
                'date':self.next_monday
            })
        with self.assertRaises(AccessError):
            self.overtime_plan_emp_01.with_user(self.user_02).unlink()
        with self.assertRaises(AccessError):
            self.overtime_plan_emp_01.with_user(self.user_02).read()
        self.assertTrue(self.overtime_plan_emp_01.with_user(self.user_01).unlink())

    def test_08_access_right_ot_plan_approval_user(self):
        """
            Case: Test access right overtime plan of Overtime Plan - Team Lead
            Expect: User in group overtime plan - team lead should have full access right (read/write/create/unlink)
                    to plan of subordinate employee.
        """
        # intenal user cannot access to other users plan.
        with self.assertRaises(AccessError):
            self.overtime_plan_emp_02.with_user(self.user_03).write({
                'date':self.next_monday
            })
        with self.assertRaises(AccessError):
            self.overtime_plan_emp_02.with_user(self.user_03).unlink()
        with self.assertRaises(AccessError):
            self.overtime_plan_emp_02.with_user(self.user_03).read()
        # approval user cannot access to plan of users, whose is not in subordinate.
        self.user_03.update({
            'groups_id': [(4, self.env.ref('viin_hr_overtime.group_overtime_team_approval').id, 0)]
        })
        with self.assertRaises(AccessError):
            self.overtime_plan_emp_02.with_user(self.user_03).write({
                'date':self.next_monday
            })
        with self.assertRaises(AccessError):
            self.overtime_plan_emp_02.with_user(self.user_03).unlink()
        with self.assertRaises(AccessError):
            self.overtime_plan_emp_02.with_user(self.user_03).read()
        # approval user have full access right (read/write/create/unlink) to plan of user, whose us in subordinate.
        self.env['ir.rule'].clear_caches()
        self.user_02.employee_id.parent_id = self.user_03.employee_id.id
        self.assertTrue(self.overtime_plan_emp_02.with_user(self.user_03).read())
        self.assertTrue(
            self.overtime_plan_emp_02.with_user(self.user_03).write(
                {
                    'date':self.next_monday
                })
        )
        self.assertTrue(self.overtime_plan_emp_02.with_user(self.user_03).unlink())

    def test_09_access_right_ot_plan_officer(self):
        """
            Case: Test access right overtime plan of Overtime Plan Line - Overtime Officer.
            Expect: User in group of overtime officer should have full access right to (read/write/create/unlink) to plan of other users
        """
        self.user_03.groups_id = [(4, self.env.ref('viin_hr_overtime.group_overtime_officer').id, 0)]
        self.assertTrue(self.overtime_plan_emp_02.with_user(self.user_03).read())
        self.assertTrue(
            self.overtime_plan_emp_02.with_user(self.user_03).write(
                {
                    'date':self.next_monday
                })
        )
        self.assertTrue(self.overtime_plan_emp_02.with_user(self.user_03).unlink())

    def test_10_access_right_ot_plan_base_admin(self):
        """
            Case: Test access right overtime plan of Administrator
            Expect: User in group of Administrator should have full access right to (read/write/create/unlink) to plan of other user.
        """
        self.user_03.groups_id = [(4, self.env.ref('viin_hr_overtime.group_overtime_admin').id, 0)]
        self.assertTrue(self.overtime_plan_emp_02.with_user(self.user_03).read())
        self.assertTrue(
            self.overtime_plan_emp_02.with_user(self.user_03).write(
                {
                    'date':self.next_monday
                })
        )
        self.assertTrue(self.overtime_plan_emp_02.with_user(self.user_03).unlink())

    #-----------------------------------------------------------Test Access Right OT mass schedule-----------------------------------------------------------#

    def test_11_access_right_internal_user(self):
        """
            Internal user cannot create overtime mass schedule.
        """
        # ensure user_01 is just an internal user without others higher level access rights
        self.user_01.groups_id = self.env.ref('base.group_user')
        with self.assertRaises(AccessError):
            self.env['hr.overtime.request.mass'].with_user(self.user_01).create({
                'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
                'mode':'department',
                'line_ids':[(0, 0, {
                        'date':self.next_monday,
                        'time_start':17.0,
                        'time_end':18.0
                    })]
            })

    def test_12_access_right_approval_team_user(self):
        """
            Approval Team user can create overtime mass schedule.
        """
        # ensure user_01 is just a OT team approver
        self.user_01.groups_id = self.env.ref('viin_hr_overtime.group_overtime_team_approval')
        self.user_02.employee_id.parent_id = self.user_01.employee_id
        involved_employees = self.user_01.employee_id | self.user_02.employee_id
        ot_request_mass = self.env['hr.overtime.request.mass'].with_user(self.user_01).create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'mode': 'employee',
            'line_ids':[(0, 0, {
                    'date':self.next_monday,
                    'time_start':17.0,
                    'time_end':18.0
                })]
        })
        self.assertEqual(
            ot_request_mass.employee_ids,
            involved_employees,
            "'Marc Demo' and 'Mike OT Bot' should be in the OT request mass"
            )
        plans = ot_request_mass._generate_overtime_plans()
        self.assertEqual(
            plans.employee_id,
            involved_employees,
            "'Marc Demo' and 'Mike OT Bot' should be in the OT plan"
            )

    def test_13_access_right_officer_user(self):
        """
            Officer user can create overtime mass schedule.
        """
        self.user_01.groups_id = [(4, self.env.ref('viin_hr_overtime.group_overtime_officer').id, 0)]
        ot_request_mass = self.env['hr.overtime.request.mass'].with_user(self.user_01).create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'mode':'department',
            'line_ids':[(0, 0, {
                    'date':self.next_monday,
                    'time_start':17.0,
                    'time_end':18.0
                })]
        })
        plans = ot_request_mass._generate_overtime_plans()
        self.assertTrue(plans and True)

    def test_14_access_right_admin_user(self):
        """
            Admin user can create overtime mass schedule.
        """
        self.user_01.groups_id = [(4, self.env.ref('viin_hr_overtime.group_overtime_officer').id, 0)]
        ot_request_mass = self.env['hr.overtime.request.mass'].with_user(self.user_01).create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'mode':'department',
            'line_ids':[(0, 0, {
                    'date':self.next_monday,
                    'time_start':17.0,
                    'time_end':18.0
                })]
        })
        plans = ot_request_mass._generate_overtime_plans()
        self.assertTrue(plans and True)
