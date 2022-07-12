from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tools import mute_logger
from odoo.tests.common import Form, tagged

from .common import Common


@tagged('-at_install','post_install')
class TestStateGroup(Common):

    def test_01_check_state_group(self):
        """
        Case 1: Kiểm tra ràng buộc model Vùng/Miền (State Group):
        - TH1:
            + Input: Tạo hoặc chọn nhóm vùng miền, thêm States thuộc Country
            + Output: Thành công
        -Th2:
            + Input: Tạo hoặc chọn nhóm vùng miền, thêm States không thuộc Country
            + Output: Thất bại, báo lỗi
        - TH3:
            + Input: Tạo hoặc chọn nhóm vùng miền, thêm Parent khác nhóm vùng miền hiện tại, cùng Country
            + Output: Thành công
        - TH4:
            + Input: Tạo hoặc chọn nhóm vùng miền, thêm Parent khác nhóm vùng miền hiện tại, khác Country
            + Output: Thất bại, báo lỗi
        - TH5:
            + Input: Tạo hoặc chọn nhóm vùng miền, thêm Parent là nhóm vùng miền hiện tại, States thuộc Country
            + Output: Thất bại, báo lỗi
        """
        # Th1: State in Country
        state_group = self.env['res.state.group'].create({
            'name': 'State Group Test',
            'code': 'SGT',
            'country_id': self.country2.id,
            'state_ids': [self.country_state2.id]
        })
        # Th2: State not in Country
        with self.assertRaises(ValidationError):
            state_group.write({'state_ids': [(4, self.country_state1.id, 0)]})
        # Th3: Parent Same country
        state_group.write({'parent_id': self.state_group2.id})
        # Th4: Parent Different country
        with self.assertRaises(ValidationError):
            state_group.write({'parent_id': self.state_group1.id})
        # Th5: Parent is itself
        with self.assertRaises(ValidationError):
            state_group.write({'parent_id': state_group.id})

    def test_02_check_state_group(self):
        """
        Case 2: Tên vùng/miền phải là duy nhất trên mỗi quốc gia
        - Input: Tạo thêm vùng/miền trùng tên và trùng quốc gia
        - Output: Tạo thất bại
        """
        with mute_logger('odoo.sql_db'):
            with self.assertRaises(IntegrityError):
                self.env['res.state.group'].create({
                    'name': 'State Group 1',
                    'code': 'SG1COPY',
                    'country_id': self.country1.id,
                    })

    def test_03_check_state_group(self):
        """
        Case 3: Tên vùng/miền phải là duy nhất trên mỗi quốc gia
        - Input: Tạo thêm vùng/miền trùng tên và khác quốc gia
        - Output: Tạo thành công
        """
        self.env['res.state.group'].create({
            'name': 'State Group 1',
            'code': 'SG1COPY',
            'country_id': self.country2.id,
            })

    def test_04_check_state_group(self):
        """
        Case 4: Mã vùng/miền phải là duy nhất trên mỗi quốc gia
        - Input: Tạo thêm vùng/miền trùng mã và trùng quốc gia
        - Output: Tạo thất bại
        """
        with mute_logger('odoo.sql_db'):
            with self.assertRaises(IntegrityError):
                self.env['res.state.group'].create({
                    'name': 'State Group 1 Copy',
                    'code': 'SG1',
                    'country_id': self.country1.id,
                    })

    def test_05_check_state_group(self):
        """
        Case 5: Mã vùng/miền phải là duy nhất trên mỗi quốc gia
        - Input: Tạo thêm vùng/miền trùng mã và khác quốc gia
        - Output: Tạo thành công
        """
        self.env['res.state.group'].create({
            'name': 'State Group 1 Copy',
            'code': 'SG1',
            'country_id': self.country2.id,
            })

    def test_onchange_state_group(self):
        """
        Case 3: Kiểm tra thay đổi của model Vùng/Miền (State Group):
        - Input:  Tạo hoặc chọn nhóm vùng miền, thêm Parent khác nhóm vùng miền hiện tại
        - Output: Country thay đổi theo country của Parent
        """
        state_group_form = Form(self.env['res.state.group'])
        state_group_form.name = 'State Group Onchange'
        state_group_form.parent_id = self.state_group1
        # Country like the country of parent
        self.assertEqual(state_group_form.country_id, self.state_group1.country_id)
