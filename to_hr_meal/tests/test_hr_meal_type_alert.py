from psycopg2 import IntegrityError

from odoo.tools.misc import mute_logger
from odoo.tests.common import SavepointCase, tagged


@tagged('-at_install', 'post_install')
class TestHrMealTypeAlert(SavepointCase):

    def test_01_hr_meal_type_alert(self):
        """
        Case 1: Giờ kế hoạch không hợp lệ
        Input: Tạo kiểu cảnh báo, nhập giờ kế hoạch là số nhỏ hơn 00:00 hoặc lớn hơn 23:59
        Output: Thất bạo -> xảy ra ngoại lệ
        """
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['hr.meal.type.alert'].create({
                'name' : 'Test 1',
                'scheduled_hour': 24,
                'message': 'test'
            })

    def test_02_hr_meal_type_alert(self):
        """
        Case 2: Giờ kế hoạch không hợp lệ
        Input: Tạo kiểu cảnh báo, nhập giờ kế hoạch là số nhỏ hơn 00:00 hoặc lớn hơn 23:59
        Output: Thất bạo -> xảy ra ngoại lệ
        """
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['hr.meal.type.alert'].create({
                'name' : 'Test 2',
                'scheduled_hour': -1,
                'message': 'test'
            })
