from unittest.mock import patch
from datetime import timedelta, date

from odoo.tests import SavepointCase


class TestMrpMaintenance(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestMrpMaintenance, cls).setUpClass()
        cls.equipment_01 = cls.env.ref('to_mrp_maintenance.equipment_furniture3').copy()
        cls.equipment_01.effective_date = date.today() - timedelta(days = 15) 
        cls.maintenance_request_01, cls.maintenance_request_02 = cls.env['maintenance.request'].create([
            {
                'name':'Request maintenance test 01',
                'equipment_id':cls.equipment_01.id,
                'request_date':date.today() - timedelta(days = 12), 
            },
            {
                'name':'Request maintenance test 02',
                'equipment_id':cls.equipment_01.id,
                'request_date':date.today() - timedelta(days = 6)               
            }
        ])

    def test_01_compute_maintenance_request(self):
        """
            Testcase 01: Kiểm tra tính toán yêu cầu bảo dưỡng.
            Input: Thiết bị không có yêu cầu bảo dưỡng nào thuộc kiểu khắc phục và ở trạng thái hoàn thành.
            Expect: - Thời gian trung bình để sửa chữa bằng 0.0
                    - Thời gian trung bình giữa 2 lần sự cố bằng 0.0
                    - Ngày sự cố gần nhất: False
                    - Thời gian dự kiến tính đến ngày sự cố tiếp theo False
        """
        self.assertEqual(self.equipment_01.mttr, 0.0)
        self.assertEqual(self.equipment_01.mtbf, 0.0)
        self.assertFalse(self.equipment_01.latest_failure_date)
        self.assertFalse(self.equipment_01.estimated_next_failure)
    
    def test_02_compute_maintenance_request(self):
        """
            Testcase 01: Kiểm tra tính toán yêu cầu bảo dưỡng.
            Input: Thiết bị có yêu cầu bảo dưỡng thuộc kiểu khắc phục và ở trạng thái hoàn thành.
        """
        self.maintenance_request_01.update({
            'stage_id':self.env.ref('maintenance.stage_3').id,
            'close_date':date.today() - timedelta(days = 9)
        })
        self.maintenance_request_02.update({
            'stage_id':self.env.ref('maintenance.stage_3').id,
            'close_date':date.today() - timedelta(days = 2)
        })
        self.assertEqual(self.equipment_01.mttr, 3)
        self.assertEqual(self.equipment_01.mtbf, 4)
        self.assertEqual(self.equipment_01.latest_failure_date, self.maintenance_request_02.request_date)
        self.assertEqual(self.equipment_01.estimated_next_failure, self.maintenance_request_02.request_date + timedelta(days = 4))
        
    def test_03_compute_maintenance_count(self):
        """
            Testcase 03: Kiểm tra tính toán số yêu cầu bảo dưỡng của lệnh sản xuất.
            Expect: Yêu cầu bảo dưỡng của lệnh sản xuất bao gồm tất cả các yêu cầu bảo dưỡng thuộc cả kiểu phòng ngừa và khắc phục ở tất cả các giai đoạn.
        """
        production_order = self.env.ref('mrp.mrp_production_1').copy()
        production_order.action_confirm()
        production_order.button_plan()
        work_order = self.env['mrp.workorder'].search([('production_id','=',production_order.id)])
        self.assertTrue(len(work_order) == 1)
        self.maintenance_request_01.update({
            'production_id':production_order.id,
            'maintenance_type':'preventive',
            'workorder_id':work_order.id
        })
        self.maintenance_request_02.update({
            'production_id':production_order.id,
            'workorder_id':work_order.id
        })
        self.assertEqual(work_order.maintenance_request_count, 2)
        self.assertEqual(production_order.maintenance_count, 2)
