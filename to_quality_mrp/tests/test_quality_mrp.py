from unittest.mock import patch
from datetime import datetime
from odoo import fields
from odoo.tests.common import tagged
from odoo.exceptions import UserError
from odoo.addons.to_quality.tests.common import Common


@tagged('-at_install', 'post_install')
class QualityMRP(Common):

    def setUp(self):
        super(QualityMRP, self).setUp()
        self.mo = self.env.ref('mrp.mrp_production_1').copy()
        self.mo.action_confirm()
        self.mo.action_assign()
        self.mo.button_plan()

    def patch_datetime_to_datetime(self, datetime):
        return patch('odoo.fields.Datetime.to_datetime', return_value=datetime)

    def test_01_check_plan_mo(self):
        """
        Case 1: Khi lên kế hoạch lệnh sản xuất sẽ tạo ra các kiểm tra chất lượng tương ứng với các hoạt động sản xuất
        """
        self.assertNotEqual(len(self.mo.workorder_ids.check_ids), 0)

    def test_11_check_done_mo(self):
        """
        Case 2: Thông báo lỗi khi hoàn thành lệnh sản xuất mà có kiểm tra chất lượng cần làm
        """
        with self.assertRaises(UserError):
            self.mo.button_mark_done()

    def test_21_check_done_wo(self):
        """
        Case 3: Thông báo lỗi khi hoàn thành hoạt đông sản xuất mà có kiểm tra chất lượng cần làm
        """
        wo = self.mo.workorder_ids[:1]
        wo.button_start()
        with self.assertRaises(UserError):
            wo.record_production()

    def test_22_check_done_wo(self):
        """
        Case 4: Tự động gắn lô vào các kiểm tra chất lượng trong hoạt động sản xuất tương ứng
        """
        wo = self.mo.workorder_ids[:1]
        for check in self.mo.workorder_ids.check_ids:
            check.do_pass()
        wo.button_start()
        self.mo.product_id.write({
            'tracking': 'lot'
        })
        lot = self.env['stock.production.lot'].create({
            'product_id': self.env.ref('product.product_product_3').id,
            'company_id': self.env.company.id
        })
        for line in wo.raw_workorder_line_ids:
            if line.product_id.tracking == 'lot':
                line.lot_id = self.env['stock.production.lot'].create({
                    'product_id': line.product_id.id,
                    'company_id': self.env.company.id
                }).id
        wo.write({
            'finished_lot_id': lot.id
        })
        with self.patch_datetime_to_datetime(datetime(2023, 8, 13, 12, 0)):
            wo.record_production()
        for lot_check in wo.check_ids:
            self.assertEqual(lot_check.lot_id, lot)

    def test_23_check_done_wo(self):
        """
        Case 5: Tự động tạo kiểm tra chất lượng khi sản xuất chưa đủ hàng
        """
        wo = self.mo.workorder_ids[:1]
        for check in self.mo.workorder_ids.check_ids:
            check.do_pass()
        wo.leave_id.date_from = datetime(2021, 8, 13, 0, 0)
        wo.button_start()
        self.mo.product_id.write({
            'tracking': 'lot'
        })
        lot = self.env['stock.production.lot'].create({
            'product_id': self.env.ref('product.product_product_3').id,
            'company_id': self.env.company.id
        })
        for line in wo.raw_workorder_line_ids:
            if line.product_id.tracking == 'lot':
                line.lot_id = self.env['stock.production.lot'].create({
                    'product_id': line.product_id.id,
                    'company_id': self.env.company.id
                }).id
        wo.write({
            'qty_producing': 2,
            'finished_lot_id': lot.id
        })
        wo.record_production()
        self.assertNotEqual(len(wo.check_ids.filtered(lambda c: c.quality_state == 'none')), 0)

    def test_31_check_count_wo(self):
        """
        Case 6: Xác thực kiểm tra chất lượng cần làm và cảnh báo chất lượng trong hoạt động sản xuất
        """
        wo = self.mo.workorder_ids[:1]
        self.assertTrue(wo.check_todo)
        self.assertEqual(wo.alert_count, 0)
