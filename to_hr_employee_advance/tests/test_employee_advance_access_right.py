from datetime import date
from odoo.tests.common import tagged
from odoo.exceptions import AccessError
from .common import Common


@tagged('-at_install', 'post_install', 'access_rights')
class TestEmployeeAdvanceAccessRights(Common):

    def setUp(self):
        super(TestEmployeeAdvanceAccessRights, self).setUp()
        # Set private address for employees
        self.employee_advance_approver_employee.write({
            'address_home_id': self.employee_advance_approver_partner.id
        })
        self.employee_advance_employee.write({
            'address_home_id': self.employee_advance_partner.id
        })

    def test_01_validate_account_user(self):
        employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 300
            })]
        })
        employee_advance.action_confirm()
        employee_advance.action_approve()
        self.account_user = self.env['res.users'].with_context(no_reset_password=True, tracking_disable=True).create({
            'name': 'Account User',
            'login': 'account',
            'groups_id': [(6, 0, self.env.ref('account.group_account_user').ids)],
        })
        employee_advance.with_user(self.account_user)
        # Check the account user rights
        employee_advance.read()
        employee_advance.write({'date': date(2021, 7, 9)})

    def test_11_validate_employee_advance_user(self):
        employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).with_user(self.employee_advance_user).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 300
            })]
        })
        employee_advance.with_user(self.employee_advance_user)
        # Check the employee advance user rights
        employee_advance.read()
        employee_advance.write({'date': date(2021, 7, 9)})
        employee_advance.unlink()

    def test_21_validate_employee_advance_approver(self):
        employee_advance_1 = self.env['employee.advance'].with_context(tracking_disable=True).with_user(self.employee_advance_approver_user).create({
            'employee_id': self.employee_advance_approver_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 300
            })]
        })
        employee_advance_1.with_user(self.employee_advance_approver_user)
        # Check the aprrover rights
        employee_advance_1.read()
        employee_advance_1.write({'date': date(2021, 7, 9)})
        employee_advance_1.unlink()

        employee_advance_2 = self.env['employee.advance'].with_context(tracking_disable=True).with_user(self.employee_advance_approver_user).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 300
            })]
        })
        employee_advance_2.with_user(self.employee_advance_approver_user)
        # Check the aprrover rights
        employee_advance_2.read()
        employee_advance_2.write({'date': date(2021, 7, 9)})
        with self.assertRaises(AccessError):
            employee_advance_2.unlink()

    def test_31_validate_employee_advance_manager(self):
        employee_advance_1 = self.env['employee.advance'].with_context(tracking_disable=True).with_user(self.employee_advance_manager_user).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 300
            })]
        })
        employee_advance_1.with_user(self.employee_advance_manager_user)
        # Check the manager rights
        employee_advance_1.read()
        employee_advance_1.write({'date': date(2021, 7, 9)})
        employee_advance_1.unlink()

        employee_advance_2 = self.env['employee.advance'].with_context(tracking_disable=True).with_user(self.employee_advance_manager_user).create({
            'employee_id': self.employee_advance_approver_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 300
            })]
        })
        employee_advance_2.with_user(self.employee_advance_manager_user)
        # Check the manager rights
        employee_advance_2.read()
        employee_advance_2.write({'date': date(2021, 7, 9)})
        employee_advance_2.unlink()

        employee_advance_3 = self.env['employee.advance'].with_context(tracking_disable=True).with_user(self.employee_advance_manager_user).create({
            'employee_id': self.employee_advance_manager_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 300
            })]
        })
        employee_advance_3.with_user(self.employee_advance_manager_user)
        # Check the manager rights
        employee_advance_3.read()
        employee_advance_3.write({'date': date(2021, 7, 9)})
        employee_advance_3.unlink()
