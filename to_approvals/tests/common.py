from odoo.tests.common import SavepointCase


class Common(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.company_a = cls.env['res.company'].create({'name': 'Company A'})
        
        cls.user_approve_admin = cls.env.ref('base.user_admin')
        cls.user_approve_officer = cls.env.ref('to_approvals.user_approve_officer_demo')
        cls.user_manager = cls.env.ref('to_approvals.user_approval_employee_manager_demo')
        cls.user_employee_1 = cls.env.ref('to_approvals.user_approval_employee_1_demo')
        cls.user_employee_2 = cls.env.ref('to_approvals.user_approval_employee_2_demo')
        cls.user_admin_company_a = cls.env.ref('to_approvals.user_approval_employee_3_demo')
        cls.user_admin_company_a.write({
            'company_id': cls.company_a.id,
            'company_ids': [(6, 0, [cls.company_a.id])]
        })
        
        # Create employee
        cls.employee_approve_admin = cls.user_approve_admin.employee_id
        cls.employee_approve_officer = cls.env['hr.employee'].create({
            'name': 'Officer',
            'user_id': cls.user_approve_officer.id,
            'parent_id': cls.employee_approve_admin.id
        })
        cls.employee_manager = cls.env['hr.employee'].create({
            'name': 'Manager',
            'user_id': cls.user_manager.id,
            'parent_id': cls.employee_approve_admin.id
        })
        cls.employee_1 = cls.env['hr.employee'].create({
            'name': 'Employee 1',
            'user_id': cls.user_employee_1.id,
            'parent_id': cls.employee_manager.id
        })
        cls.employee_2 = cls.env['hr.employee'].create({
            'name': 'Employee 2',
            'user_id': cls.user_employee_2.id,
            'parent_id': cls.employee_1.id
        })
        cls.employee_3 = cls.env['hr.employee'].create({
            'name': 'Employee 3',
            'parent_id': cls.employee_approve_admin.id,
        })

        cls.approve_type_no_valid = cls._create_type(name='No Validation')
        cls.approve_type_hr = cls._create_type(
            name='HR Approve', 
            responsible_id= cls.user_approve_officer.id, 
            validation_type='hr'
        )
        cls.approve_type_leader = cls._create_type(name='Manager Approve',validation_type='leader')
        cls.approve_type_both = cls._create_type(
            name='Manager & HR', 
            responsible_id= cls.user_approve_officer.id, 
            validation_type='both'
        )
        
        # Employee create approve request
        cls.approve_request_employee = cls.env['approval.request'].create({
            'title': 'Employee Request 1',
            'employee_id': cls.employee_1.id,
            'approval_type_id': cls.approve_type_no_valid.id,
        })
        
        cls.approve_request_employee_2 = cls.env['approval.request'].create({
            'title': 'Employee Request 2',
            'employee_id': cls.employee_2.id,
            'approval_type_id': cls.approve_type_no_valid.id,
        })
        
        cls.approve_request_employee_3 = cls.env['approval.request'].create({
            'title': 'Employee Request 3',
            'employee_id': cls.employee_3.id,
            'approval_type_id': cls.approve_type_no_valid.id,
        })
    
    @classmethod
    def _create_type(cls, name, responsible_id=False, type='generic', validation_type='no_validation'):
        return cls.env['approval.request.type'].create({
            'name': name,
            'type': type,
            'validation_type': validation_type,
            'responsible_id': responsible_id
        })
