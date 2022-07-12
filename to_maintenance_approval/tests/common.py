from odoo.addons.to_approvals.tests.common import Common


class CommonMaintenanceApproval(Common):
    
    @classmethod
    def setUpClass(cls):
        super(CommonMaintenanceApproval, cls).setUpClass()
        cls.equipment_1 = cls.env['maintenance.equipment'].create({
            'name': 'Equiment 1',
            'employee_id': cls.employee_1.id
        })
        
        cls.approve_type_no_valid = cls._create_type(
            name='No Validation',
            type='maintenance_type'
        )
        cls.approve_type_hr = cls._create_type(
            name='HR Approve',
            type='maintenance_type',
            responsible_id=cls.user_approve_officer.id,
            validation_type='hr'
        )
        cls.approve_type_leader = cls._create_type(
            name='Manager Approve',
            type='maintenance_type',
            validation_type='leader'
        )
        cls.approve_type_both = cls._create_type(
            name='Manager & HR',
            type='maintenance_type',
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
