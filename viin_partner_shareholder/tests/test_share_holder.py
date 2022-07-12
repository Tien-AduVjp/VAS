from psycopg2._psycopg import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tools.misc import mute_logger

from .common import Common


@tagged('post_install', '-at_install')
class TestShareHolder(Common):

    #Case 1
    def test_create_new_contact(self):
        """
        INPUT: Tạo mới 1 liên hệ, thêm thông tin cổ đông cho liên hệ
        OUTPUT: Thông tin cổ đông được gắn với liên hệ
        """
        self.assertEqual(self.contact_a.shareholder_ids.id, self.share_holder_1.id)

    #Case 2
    def test_write_type_company(self):
        """
        INPUT: Thay đổi kiểu công ty của liên hệ từ công ty sang cá nhân
        OUTPUT: Thông tin cổ đông sẽ biến mất
        """
        self.contact_a.write({
            'is_company': False,
            })
        self.assertFalse(self.contact_a.shareholder_ids, "shareholder_ids is not False")

    #Case 3
    def test_constraint_ownership_rate(self):
        """
        INPUT: Đặt giá trị cổ phần cho cổ đông
        OUTPUT: Nếu cổ phần có giá trị nhỏ hơn 0
                hoặc lớn hơn 100 sẽ thông báo lỗi
        """
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            record_1 = self.env['res.partner.shareholder'].create({
                'partner_id' : self.env.ref('base.res_partner_18').id,
                'shareholder_id': self.env.ref('base.res_partner_address_14').id,
                'ownership_rate': -1.00
            })
            record_1.write({
                'ownership_rate': 999
                })

    #Case 4
    def test_constraint_total_ownership_rate(self):
        """
        INPUT: Đặt các giá trị cổ phần cho cổ đông
        OUTPUT: Nếu tổng cổ phần có giá trị lớn hơn 100 sẽ thông báo lỗi
        """
        with self.assertRaises(ValidationError):
            record_2 = self.env['res.partner.shareholder'].create({
                'partner_id' : self.env.ref('base.res_partner_2').id,
                'shareholder_id': self.env.ref('base.res_partner_address_14').id,
                'ownership_rate': 99.00
            })
            record_3 = self.env['res.partner.shareholder'].create({
                'partner_id' : self.env.ref('base.res_partner_2').id,
                'shareholder_id': self.env.ref('base.res_partner_address_16').id,
                'ownership_rate': 99.00
            })

    #Case 5
    def test_constraint_partner_id(self):
        """
        INPUT: Tạo record cho Shareholder vởi partner_id là 'person'
        OUTPUT: Thông báo lỗi contraint
        """
        with self.assertRaises(ValidationError):
            record_shareholder_test = self.env['res.partner.shareholder'].create({
                'partner_id' : self.env.ref('base.res_partner_address_16').id,
                'shareholder_id': self.env.ref('base.res_partner_address_10').id,
                'ownership_rate': 99.00
            })

    #Case 6
    def test_check_shareholder_ids(self):
        """
        INPUT: Tạo một Partner mới với company_type là 'person' và đã có thông tin cổ đông
        OUTPUT: Thông báo lỗi contraint
        """
        with self.assertRaises(ValidationError):
            record_partner_test = self.env['res.partner'].with_context(tracking_disable=True).create({
                'name':'Contact A',
                'company_type': 'person',
            })

            record_shareholder_test = self.env['res.partner.shareholder'].create({
                'partner_id' : record_partner_test.id,
                'shareholder_id': self.env.ref('base.res_partner_address_10').id,
                'ownership_rate': 99.00
            })

    #Case 7
    def test_insert_shareholder_from_other_company(self):
        """
        INPUT:
            Công ty A đang có tổng cổ phần là 100%
            Tại công ty B, thêm một bản ghi cho cổ đông của công ty A
        OUTPUT:
            Thông báo lỗi tổng số cổ phần của công ty A
        """
        with self.assertRaises(ValidationError):
            self.share_holder_1.write({
                'ownership_rate': 100
                })
            self.share_holder_2.write({
                'ownership_rate': 100,
                'partner_id' : self.contact_a.id,
                })
