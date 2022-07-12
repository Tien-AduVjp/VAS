from datetime import date
from odoo.tests.common import tagged
from odoo.exceptions import AccessError
from .common import Common


@tagged('-at_install', 'post_install', 'access_rights')
class TestEmployeeAdvanceAccessRights(Common):

    def setUp(self):
        super(TestEmployeeAdvanceAccessRights, self).setUp()
        # Create company B
        company_b = self.env['res.company'].create({
            'name': 'Company B',
        })
        self.employee_advance_user_b = self.env['res.users'].with_context(no_reset_password=True, tracking_disable=True).create({
            'name': 'User B',
            'login': 'User B',
            'company_ids': [(6, 0, company_b.ids)],
            'company_id': company_b.id,
            'groups_id': [(6, 0, [
                self.env.ref('to_hr_employee_advance.group_employee_advance_user').id])],
        })

    def test_01_multi_company(self):
        self.employee_advance_employee.write({
            'address_home_id': self.employee_advance_partner.id
        })
        employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 300
            })]
        })
        with self.assertRaises(AccessError):
            employee_advance.with_user(self.employee_advance_user_b).read()
        with self.assertRaises(AccessError):
            employee_advance.with_user(self.employee_advance_user_b).write({'date': date(2021, 7, 9)})
        with self.assertRaises(AccessError):
            self.env['employee.advance'].with_context(tracking_disable=True).with_user(self.employee_advance_user_b).create({
                'employee_id': self.employee_advance_employee.id,
                'date': date(2021, 7, 10),
                'journal_id': self.advance_journal.id,
                'lines': [(0, 0, {
                    'name': 'Advance Line 1',
                    'amount': 300
                })]
            })
        with self.assertRaises(AccessError):
            employee_advance.with_user(self.employee_advance_user_b).unlink()

        employee_advance.action_confirm()
        employee_advance.action_approve()

        employee_advance_reconcile = self.env['employee.advance.reconcile'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_manager_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
        })
        with self.assertRaises(AccessError):
            employee_advance_reconcile.with_user(self.employee_advance_user_b).read()
        with self.assertRaises(AccessError):
            employee_advance_reconcile.with_user(self.employee_advance_user_b).write({'date': date(2021, 7, 9)})
        with self.assertRaises(AccessError):
            self.env['employee.advance.reconcile'].with_context(tracking_disable=True).with_user(self.employee_advance_user_b).create({
                'employee_id': self.employee_advance_manager_employee.id,
                'date': date(2021, 7, 10),
                'journal_id': self.advance_journal.id,
            })
        with self.assertRaises(AccessError):
            employee_advance_reconcile.with_user(self.employee_advance_user_b).unlink()
