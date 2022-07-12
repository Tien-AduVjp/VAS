from functools import partial
from odoo.tests import new_test_user, SingleTransactionCase, tagged

hr_seniority_new_user = partial(new_test_user, context={
    'mail_create_nolog': True,
    'mail_create_nosubscribe': True,
    'mail_notrack': True,
    'no_reset_password': True
})


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccessRights, cls).setUpClass()

        cls.HrEmployeeSeniority = cls.env['hr.employee.seniority']

        cls.employee_personal = cls.env.ref('hr.employee_stw')
        cls.user_personal = hr_seniority_new_user(cls.env, login='user_personal', groups='base.group_user', employee_ids=[(4, cls.employee_personal.id)])

        cls.employee_manager = cls.env.ref('hr.employee_al')
        cls.user_manager = hr_seniority_new_user(cls.env, login='user_manager', groups='base.group_user', employee_ids=[(4, cls.employee_manager.id)])

        cls.user_hr = cls.env.ref('base.user_admin')

        some_company = cls.env['res.company'].create({'name': 'Some Company'})
        cls.user_multi_company = hr_seniority_new_user(cls.env, login='user_multi_company', groups='hr.group_hr_user',
                                                       company_id=some_company.id, company_ids=[(6, 0, some_company.ids)])

    def test_access_rights(self):
        """Case 1: User belongs to group 'base.group_user'
                Expectation: only see their seniority
        """
        seniority_personal = self.HrEmployeeSeniority.with_user(self.user_personal).search([])
        self.assertEqual(seniority_personal, self.user_personal.employee_id.employee_seniority_ids)

        """Case 2: User belongs to group 'base.group_user' and is manager
                Expectation: Only see their seniority and the seniority of the staff they manage
        """
        seniority_manager = self.HrEmployeeSeniority.with_user(self.user_manager).search([])
        expectation_seniority = self.env['hr.employee'] \
            .search(['|', ('parent_id', '=', self.employee_manager.id), ('id', '=', self.employee_manager.id)]) \
            .mapped('employee_seniority_ids')
        self.assertEqual(seniority_manager, expectation_seniority)

        """Case 3: User belongs to group 'hr.group_hr_user'
                Expectation: See all staff's seniority
        """
        seniority_user_hr = self.HrEmployeeSeniority.with_user(self.user_hr).search([])
        expectation_seniority = self.env['hr.employee'].search([]).mapped('employee_seniority_ids')
        self.assertEqual(seniority_user_hr, expectation_seniority)

        """Case 3: User belongs to group 'hr.group_hr_user' but different company
                Expectation: Don't see anything
        """
        seniority_user_hr = self.HrEmployeeSeniority.with_user(self.user_multi_company).search([])
        self.assertEqual(len(seniority_user_hr), 0)
