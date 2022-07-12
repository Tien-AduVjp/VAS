from odoo.tests.common import tagged
from odoo.exceptions import UserError
from odoo.addons.to_quality.tests.common import Common


@tagged('-at_install', 'post_install')
class QualityMRP(Common):

    def setUp(self):
        super(QualityMRP, self).setUp()
        self.mo = self.env.ref('mrp.mrp_production_3').copy()
        self.mo.action_confirm()
        self.mo.action_assign()
        self.mo.button_plan()

    def test_01_check_plan_mo(self):
        """
        Case 1: Khi xác nhân một lệnh sản xuất sẽ tạo ra kiểm tra chất lượng nguyên vật liệu cho từng hoạt động sản xuất
        """
        wo_1 = self.mo.workorder_ids[:1]
        self.assertTrue(wo_1.check_ids)
        with self.assertRaises(UserError):
            wo_1.button_start()

    def test_11_check_done_mo(self):
        """
        Case 2: Thông báo lỗi khi hoàn thành lệnh sản xuất mà có kiểm tra chất lượng cần làm
        """
        with self.assertRaises(UserError):
            self.mo.button_mark_done()

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
        wo.write({
            'finished_lot_id': lot.id
        })
        wo.check_ids.do_pass()
        wo.button_finish()
        for lot_check in wo.check_ids:
            self.assertEqual(lot_check.lot_id, lot)
