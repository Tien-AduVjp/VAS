from odoo.tests.common import SavepointCase


class Common(SavepointCase):
    def setUp(self):
        super(Common, self).setUp()
        #company
        self.company_demo_rank = self.env['res.company'].create({'name': 'Company demo rank'})
        #department
        self.department_1 = self.env['hr.department'].create({'name' : 'Department 1'})
        self.department_2 = self.env['hr.department'].create({'name' : 'Department 2'})
        #role
        self.role_demo_1 = self.env['hr.role'].with_context(tracking_disable=True).create({
            'name': 'Role 1',
            'department_id' : self.department_1.id
            })
        self.role_demo_2 = self.env['hr.role'].with_context(tracking_disable=True).create({
            'name': 'Role 2'
            })
        #grade
        self.grade_demo_1 = self.env['hr.employee.grade'].with_context(tracking_disable=True).create({
            'name': 'Level 1'
            })
        self.grade_demo_2 = self.env['hr.employee.grade'].with_context(tracking_disable=True).create({
            'name': 'Level 2'
            })
        #rank
        self.rank_demo_1 = self.env['hr.rank'].with_context(tracking_disable=True).create({
            'role_id' : self.role_demo_1.id,
            'grade_id': self.grade_demo_1.id
            })
        #job rank lines
        self.job_1 = self.env['hr.job'].with_context(tracking_disable=True).create({
            'name' : 'Job 1'
            })
        self.job_2 = self.env['hr.job'].with_context(tracking_disable=True).create({
            'name' : 'Job 2'
            })
        self.job_rank_line_1 = self.env['hr.job.rank.line'].with_context(tracking_disable=True).create({
            'job_id' : self.job_1.id,
            'role_id' : self.role_demo_1.id,
            'grade_id' : self.grade_demo_1.id
            })
        #user
        self.user_employee_rank = self.env['res.users'].with_context({
            'no_reset_password': True,                                                 
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'Employee user Rank',
                'login': 'user_employee_rank',
                'email': 'userhrrank@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

        self.user_hr_officer_rank = self.env['res.users'].with_context({
            'no_reset_password': True,                                                 
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'HR Officer user Rank',
                'login': 'hr_officer',
                'email': 'userofficerrank@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('hr.group_hr_user').id])],
        })

        self.user_multicomp_rank = self.env['res.users'].with_context({
            'no_reset_password': True,                                                 
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'Multi Company User Rank',
                'login': 'user_multi_comp_rank',
                'email': 'usermulti@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('hr.group_hr_user').id])],
                'company_id' : self.company_demo_rank.id,
                'company_ids' : [(6, 0, self.company_demo_rank.ids)],
            })
