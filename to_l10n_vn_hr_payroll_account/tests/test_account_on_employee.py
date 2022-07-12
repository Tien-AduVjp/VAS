from odoo.tests import tagged

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestAccountOnEmployee(TestCommon):

    def test_01_account_on_employee(self):
        """Case 1: Test thông tin kế toán của nhân viên
        Input: Truy cập địa chỉ riêng tư của nhân viên
            TH2: Nhân viên có thiết lập địa chỉ riêng tư, công ty có thiết lập COA Việt Nam
        Output:
            TH2: Tab Invoincing trên địa chỉ riêng tư, Tài khoản phải trả: 3341 Phải trả nhân viên
        """
        """Case 3: Sửa địa chỉ riêng tư của nhân viên của công ty có thiết lập COA Việt Nam
        Input: Sửa địa chỉ riêng tư của nhân viên
            TH2: Có thiết lập trường "Địa chỉ"  hợp lệ trong tab "Thông tin riêng tư"
        Output:
            TH2: Địa chỉ mới được cập nhật thông tin tài khoản kế toán:
            Tài khoản phải trả: 3341 Phải trả nhân viên
        """
        address_home_id = self.env['res.partner'].with_context(tracking_disable=True).create({
            'name': 'partner test 1',
            'country_id': self.env.ref('base.vn').id
            })
        self.assertEqual(address_home_id.property_account_payable_id.code, '331')
        employee1 = self.env['hr.employee'].with_context(tracking_disable=True).create({
            'name': 'employee test 1',
            'address_home_id': address_home_id.id,
            })

        self.assertEqual(employee1.address_home_id.property_account_payable_id.code, '3341')
