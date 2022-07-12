from odoo.tests.common import tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestResParner(Common):

    def test_01_check_partner(self):
        """
        Kiểm tra khi thay đổi Bang/Tỉnh trên Contact
        - Input: Tạo Contact, lựa chọn Bang/Tỉnh
        - Output: Nhóm vùng miền tự đồng điền tương ứng với nhóm vùng miền của Bang/Tỉnh
        """
        partner = self.env['res.partner'].create({
            'name': 'Partner Test',
            'state_id': self.country_state1.id,
            'company_id': self.env.company.id
        })
        self.assertEqual(partner.state_group_id, partner.state_group_id)
