from unittest.mock import patch
from psycopg2 import IntegrityError

from odoo import fields
from odoo.tools.misc import mute_logger
from odoo.tests.common import tagged
from odoo.exceptions import ValidationError

from .common import Common


@tagged('-at_install', 'post_install')
class TestMaintenanceEquipment(Common):

    @patch.object(fields.Date, 'context_today', lambda *arg, **kwarg: fields.Date.to_date('2021-12-08'))
    def test_maintenance_equipment_1(self):
        """
        Case 1: Kiểm tra thay đổi thiết bị khi có Thời gian làm việc trung bình hàng ngày của thiết bị và Tần suất bảo trì phòng ngừa
        Input:
        Tạo mới hoặc chọn Thiết bị có:
            - Thời gian làm việc trung bình hàng ngày: 8 Giờ
            - Thời gian giữa các lần bảo trì: 24 Giờ
        Output:
            - Tần suất bảo trì phòng ngừa: 3 Ngày
            - Ngày bảo trì phòng ngừa tiếp theo: 2021-12-11
        """
        self.equipment.write({
            'ave_daily_working_hours': 8,
            'working_hour_period': 24,
        })
        self.assertRecordValues(self.equipment, [{'period': 3, 'next_action_date': fields.Date.to_date('2021-12-11')}])

    def test_maintenance_equipment_2(self):
        """
        Case 2: Kiểm tra thay đổi khi có Thời gian làm việc trung bình hàng ngày của thiết bị và Tần suất bảo trì phòng ngừa
        Input:
        Chọn hoặc tạo Thiết bị chỉ nhập Thời gian làm việc trung bình hàng ngày hoặc Thời gian giữa các lần bảo trì
        Output:
            - Tần suất bảo trì phòng ngừa: 0 Ngày
            - Ngày bảo trì phòng ngừa tiếp theo: False
        """
        self.equipment.write({
            'ave_daily_working_hours': 8,
        })
        self.assertRecordValues(self.equipment, [{'period': 0, 'next_action_date': False}])

    def test_maintenance_equipment_3(self):
        """
        Case 3: Kiểm tra khi thiết bị có Thời gian làm việc trung bình hàng ngày của thiết bị hoặc Tần suất bảo trì phòng ngừa
        nhưng không có nhóm bảo trì
        Input:
        Chọn hoặc tạo Thiết bị có Thời gian làm việc trung bình hàng ngày hoặc Thời gian giữa các lần bảo trì, nhưng không chọn
        nhóm bảo trì thiết bị
        Output: Xảy ra ngoại lệ
        """
        with self.assertRaises(ValidationError):
            self.equipment.write({
                'ave_daily_working_hours': 8,
                'maintenance_team_id': False
            })

    def test_constraints_maintenance_equipment_1(self):
        """
        Case 4: Kiểm tra ràng khi nhập dữ liệu là số âm cho Thời gian làm việc trung bình hàng ngày hoặc Thời gian giữa các lần bảo trì
        Input:
            - Thời gian làm việc trung bình hàng ngày: -8 Giờ
            - Thời gian giữa các lần bảo trì: -24 Giờ
        Output:
            Xảy ra ngoại lệ
        """
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.equipment.write({
                'ave_daily_working_hours': -8,
                'working_hour_period': -24
            })
            self.equipment.flush()

    def test_constraints_maintenance_equipment_2(self):
        """
        Case 5: Kiểm tra ràng khi nhập dữ liệu là số dương cho Thời gian làm việc trung bình hàng ngày
        hoặc Thời gian giữa các lần bảo trì
        Input:
            - Thời gian làm việc trung bình hàng ngày: 8 Giờ
            - Thời gian giữa các lần bảo trì: 24 Giờ
        Output: Thành công
        """
        self.equipment.write({
            'ave_daily_working_hours': 8,
            'working_hour_period': 24
        })
        self.equipment.flush()
