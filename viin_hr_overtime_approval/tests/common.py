from datetime import date

from odoo.addons.to_approvals.tests.common import Common


class CommonOverTimeApproval(Common):
    
    @classmethod
    def setUpClass(cls):
        super(CommonOverTimeApproval, cls).setUpClass()
        cls.approve_type_no_valid = cls._create_type(
            name = 'No Validation',
            type = 'overtime'
        )
        cls.approve_type_hr = cls._create_type(
            name = 'HR Approve',
            type = 'overtime',
            responsible_id = cls.user_approve_officer.id,
            validation_type = 'hr'
        )
        cls.approve_type_leader = cls._create_type(
            name = 'Manager Approve',
            type = 'overtime',
            validation_type = 'leader'
        )
        cls.approve_type_both = cls._create_type(
            name = 'Manager & HR',
            type = 'overtime',
            responsible_id = cls.user_approve_officer.id,
            validation_type = 'both'
        )
        # Invalidate cache to avoid cache storage problem
        cls.approve_type_no_valid.invalidate_cache()
        cls.approve_type_hr.invalidate_cache()
        cls.approve_type_leader.invalidate_cache()
        cls.approve_type_both.invalidate_cache()
        
        # Contract Employee
        cls.contract_1 = cls.env['hr.contract'].create({
            'name': 'Employee 1',
            'employee_id': cls.employee_1.id,
            'wage': 10000000.0,
            'date_start': date(2021, 10, 10),
            'date_end': date.max,
            'state': 'open'
        })
        cls.contract_2 = cls.env['hr.contract'].create({
            'name': 'Employee 2',
            'employee_id': cls.employee_2.id,
            'wage': 10000000.0,
            'date_start': date(2021, 10, 10),
            'date_end': date.max,
            'state': 'open'
        })
        
        # Overtime Approval Type: type that only supports test cases
        cls.approve_type_overtime = cls._create_type(
            name='Overtime Approval Test',
            type='overtime',
            responsible_id=cls.user_approve_officer.id,
            validation_type='both'
        )
        # Generic Approval Type: type that only supports test cases
        cls.approve_type_generic = cls._create_type(
            name='Generic Test',
            type='generic'
        )
        
        # Overtime Approval: only supports test cases
        cls.overtime_approval_request = cls.env['approval.request'].create({
            'title': 'Overtime Approval Request Test',
            'employee_id': cls.env.ref('base.user_admin').employee_id.id,
            'approval_type_id': cls.approve_type_overtime.id,
        })
        
        #Reason Overtime
        cls.reason_general = cls.env.ref('viin_hr_overtime.hr_overtime_reason_general')
        
        # Overtime Plan
        cls.overtime_plan_1 = cls.env['hr.overtime.plan'].create({
            'employee_id': cls.employee_1.id,
            'recognition_mode': 'none',
            'reason_id': cls.reason_general.id,
            'time_start': 17,
            'time_end': 18,
        })
        cls.overtime_plan_2 = cls.env['hr.overtime.plan'].create({
            'employee_id': cls.employee_1.id,
            'recognition_mode': 'none',
            'reason_id': cls.reason_general.id,
            'time_start': 18,
            'time_end': 19,
        })
        cls.overtime_plan_3 = cls.env['hr.overtime.plan'].create({
            'employee_id': cls.employee_2.id,
            'recognition_mode': 'none',
            'reason_id': cls.reason_general.id,
            'time_start': 17,
            'time_end': 18,
        })
