from odoo.tests.common import SavepointCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class HrTestEmployeeCommon(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create user.
        # User has group 'group_hr_user'
        cls.user_hr_user = cls.env['res.users'].create({
            'name': 'Because I am hruser!',
            'login': 'hruser@viindoo.com',
            'groups_id': [(4, cls.env.ref('hr.group_hr_user').id),
                           (4, cls.env.ref('base.group_private_addresses').id),
                           (4, cls.env.ref('base.group_no_one').id),
                           (4, cls.env.ref('base.group_partner_manager').id)]
            })
        cls.user_hr_user.partner_id.email = 'hrman@viindoo.com'
        # User has group 'group_hr_manager'
        cls.user_hr_admin = cls.env['res.users'].create({
            'name': 'Because I am hradmin!',
            'login': 'hradmin@viindoo.com',
            'groups_id': [(4, cls.env.ref('hr.group_hr_manager').id), 
                          (4, cls.env.ref('base.group_private_addresses').id),
                          (4, cls.env.ref('base.group_no_one').id),
                          (4, cls.env.ref('base.group_partner_manager').id)]
            })
        # Internal User
        cls.user = cls.env['res.users'].create({
            'name': 'Because I am userman!',
            'login': 'userman@viindoo.com',
            'groups_id': [(4, cls.env.ref('base.group_user').id)]
            })
        cls.user.partner_id.email = 'testman@viindoo.com'
        
        # =======Partners=========
        cls.partner = cls.user.partner_id
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'partner_a',
            'company_id': False
        })
        
        # =======Applicant========
        cls.applicant_a = cls.env['hr.applicant'].create({
            'name': 'Applicant Man',
            'partner_name': 'Applicant Man'
            })
        cls.applicant_a.create_employee_from_applicant()
        
        cls.applicant_b = cls.env['hr.applicant'].create({
            'name': 'Applicant Woman',
            'partner_name': 'Applicant Woman',
            'email_from': 'applicant.woman@example.viindoo.com'
            })
        # =======Employee=========
        cls.employee_a = cls.applicant_a.emp_id
