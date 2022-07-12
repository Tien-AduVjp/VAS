from datetime import date

from odoo.addons.to_approvals.tests.common import Common


class CommonTimesheetApproval(Common):
    
    @classmethod
    def setUpClass(cls):
        super(CommonTimesheetApproval, cls).setUpClass()
        cls.department_a = cls.env['hr.department'].create({
            'name': 'Department A',
            'timesheet_approval': True
        })
        cls.department_b = cls.env['hr.department'].create({
            'name': 'Department B',
            'parent_id': cls.department_a.id
        })

        cls.job_position_1 = cls.env['hr.job'].create({
            'name': 'Job 1',
        })
        
        cls.contract_1 = cls.env['hr.contract'].create({
            'name': 'Employee 1',
            'employee_id': cls.employee_1.id,
            'wage': 10000000.0,
            'date_start': date(2021, 10, 10),
            'date_end': date.max,
            'timesheet_approval': True,
            'state': 'open'
        })
        
        cls.project = cls.env.ref('project.project_project_2')
        
        cls.timesheet_1 = cls.env['account.analytic.line'].create({
            'name': 'Timesheet Employee 1',
            'project_id': cls.project.id,
            'employee_id': cls.employee_1.id,
            'unit_amount': 1,
        })
        cls.timesheet_2 = cls.env['account.analytic.line'].create({
            'name': 'Timesheet Employee 1',
            'project_id': cls.project.id,
            'employee_id': cls.employee_1.id,
            'unit_amount': 2,
        })
        cls.timesheet_3 = cls.env['account.analytic.line'].create({
            'name': 'Timesheet Employee 2',
            'project_id': cls.project.id,
            'employee_id': cls.employee_2.id,
            'unit_amount': 1,
        })
        cls.timesheet_4 = cls.env['account.analytic.line'].create({
            'name': 'Timesheet Employee Officer',
            'project_id': cls.project.id,
            'employee_id': cls.employee_approve_officer.id,
            'unit_amount': 1,
        })
        
        cls.approve_type_no_valid = cls._create_type(
            name='No Validation',
            type='timesheets'
        )
        cls.approve_type_hr = cls._create_type(
            name='HR Approve',
            type='timesheets',
            responsible_id=cls.user_approve_officer.id,
            validation_type='hr'
        )
        cls.approve_type_leader = cls._create_type(
            name='Manager Approve',
            type='timesheets',
            validation_type='leader'
        )
        cls.approve_type_both = cls._create_type(
            name='Manager & HR',
            type='timesheets',
            responsible_id=cls.user_approve_officer.id,
            validation_type='both'
        )
        # type that only supports test cases
        cls.approve_type_generic = cls._create_type(
            name='Generic',
            type='generic'
        )
        
        # Invalidate cache to avoid cache storage problem
        cls.approve_type_no_valid.invalidate_cache()
        cls.approve_type_hr.invalidate_cache()
        cls.approve_type_leader.invalidate_cache()
        cls.approve_type_both.invalidate_cache()
