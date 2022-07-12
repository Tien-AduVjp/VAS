from odoo.tests.common import tagged
from odoo.exceptions import AccessError

from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):
    
    def test_access_voucher(self):
        voucher = self.voucher.move_finished_ids.move_line_ids.voucher_id[0]
        voucher.with_user(self.group_pos_user).read()
        voucher.with_user(self.group_pos_user).write({
            'serial': 'W3148748485'
        })
        with self.assertRaises(AccessError):
            voucher.with_user(self.group_pos_user).unlink()  
        with self.assertRaises(AccessError):
            self.env['voucher.voucher'].with_user(self.group_pos_user).create({
                'name': 'SP_VOUCHER/0000083',
                'serial': '187408302334'
            })   
