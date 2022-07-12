from odoo.tests import tagged

from .common import HrTestEmployeeCommon


@tagged('post_install', '-at_install')
class TestPartner(HrTestEmployeeCommon):

    def test_compute_employee_ids(self):
        user_a = self.env['res.users'].create({
            'name': 'User Vendor Bot',
            'login': 'user_vendor_bot',
            'email': 'user.vendor.bot@vendor.com',
            'partner_id': self.partner_a.id,
        })
        self.employee.write({'user_id': user_a.id})
        self.assertTrue(self.employee.id in user_a.partner_id.employee_ids.ids,
                        "viin_hr: Error compute_employee_ids")

    def test_compute_is_employee(self):
        self.assertTrue(self.partner_a.employee,
                        "viin_hr: Error compute_is_employee")

