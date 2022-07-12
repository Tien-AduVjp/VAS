from odoo.exceptions import AccessError
from odoo.tests.common import tagged

from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):
    
    #Case 1
    def test_partner_manager_access_right(self):
        """
        Tài khoản manager có quyền: Tạo mới, đọc, cập nhật, xoá thông tin của cổ đông
        """
        share_holder_test = self.env['res.partner.shareholder'].with_user(self.user_partner_manager).create({
            'partner_id' : self.contact_a.id,
            'shareholder_id': self.env.ref('base.res_partner_10').id,
            'owned_percentage': 12,
            'description': 'test'
        })
        share_holder_test.with_user(self.user_partner_manager).read()
        share_holder_test.with_user(self.user_partner_manager).write({
            'owned_percentage': 15,
        })
        share_holder_test.with_user(self.user_partner_manager).unlink()
        
    #Case 2
    def test_internal_user_access_right(self):
        """
        Tài khoản nội bộ, không có quyền tạo liên hệ. 
        Chỉ có quyền đọc thông tin của cổ đông
        Không có quyền tạo mới, cập nhật, xoá thông tin của cổ đông
        """
        self.share_holder.with_user(self.user_internal).read()
        with self.assertRaises(AccessError):
            share_holder_test = self.env['res.partner.shareholder'].with_user(self.user_internal).create({
                'shareholder_id': self.env.ref('base.res_partner_10').id,
                'owned_percentage': 12,
                'description': 'test'
            })
        with self.assertRaises(AccessError):
            self.share_holder.with_user(self.user_internal).write({'owned_percentage': 15})
        with self.assertRaises(AccessError):
            self.share_holder.with_user(self.user_internal).unlink()
