from odoo.tests import TransactionCase


class TestUserAssignmentLogCommon(TransactionCase):
    
    def setUp(self):
        super(TestUserAssignmentLogCommon, self).setUp()
        
        self.autovacuum_job = self.env.ref('base.autovacuum_job')
        self.main_company = self.env.ref('base.main_company')        
        self.company_B = self.env['res.company'].create({'name': 'Company B'})    
        self.user_admin = self.env.ref('base.user_admin')
        self.env.ref('base.model_ir_cron').write({'track_user_assignment': True})
        self.env.ref('base.model_res_partner').write({'track_user_assignment': True})
        
        Users = self.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True, 'mail_create_nolog': True})
        self.employee_user_main_comp = Users.create({
            'name': 'Employee User Comp Main',
            'login': 'EmployeeCompMain',
            'email': 'employeeuser_comp_main@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
            'company_id': self.main_company.id,
            'company_ids': [(4, self.main_company.id)]
        })
        self.employee_user_comp_B = Users.create({
            'name': 'Employee User Comp B',
            'login': 'EmployeeCompB',
            'email': 'employeeuser_comp_b@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
            'company_id': self.company_B.id,
            'company_ids': [(4, self.company_B.id)]
        })
