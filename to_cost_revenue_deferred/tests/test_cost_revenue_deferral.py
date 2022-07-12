from odoo.tests import Form, tagged
from odoo import fields
from odoo.exceptions import ValidationError, UserError
from .common import Common


@tagged('post_install', '-at_install')
class TestCostRevenueDeferral(Common):

    def test_deferral_category_onchange_journal_01(self):
        """
        Trên form của Nhóm Phân bổ Doanh thu chọn sổ nhật ký, chọn sổ nhật ký
            Output: tài khoản phân bổ thay đổi theo Tài khoản ghi nợ mặc định của sổ nhật ký
        """
        f = Form(self.env['cost.revenue.deferral.category'].with_context(default_move_type='revenue'), view="to_cost_revenue_deferred.revenue_deferral_category_form")
        f.journal_id = self.journal_revenue_deferral
        self.assertEqual(f.deferred_account_id, self.journal_revenue_deferral.default_account_id)

    def test_deferral_category_onchange_journal_02(self):
        """
        Trên form của Nhóm Phân bổ Chi phí chọn sổ nhật ký, chọn sổ nhật ký
            Output: tài khoản phân bổ thay đổi theo Tài khoản ghi có mặc định của sổ nhật ký
        """
        f = Form(self.env['cost.revenue.deferral.category'].with_context(default_move_type='cost'), view="to_cost_revenue_deferred.cost_deferral_category_form")
        f.journal_id = self.journal_cost_deferral
        self.assertEqual(f.deferred_account_id, self.journal_cost_deferral.default_account_id)

    def test_deferral_onchange_deferral_category_id(self):
        """
        Các trường trên form của phân bổ chi phí/ doanh thu thay đổi theo các trường của Nhóm Phân bổ chi/ doanh thu
        """
        f = Form(self.env['cost.revenue.deferral'].with_context(default_move_type='revenue'), view="to_cost_revenue_deferred.cost_revenue_deferral_form")
        f.deferral_category_id = self.revenue_deferral_category
        self.assertEqual(f.method_time, 'number')
        self.assertEqual(f.method_number, self.revenue_deferral_category.method_number)
        self.assertEqual(f.method_period, self.revenue_deferral_category.method_period)

        f.deferral_category_id = self.revenue_deferral_category_end
        self.assertEqual(f.method_time, 'end')
        self.assertEqual(f.method_end, self.revenue_deferral_category_end.method_end)
        self.assertEqual(f.method_period, self.revenue_deferral_category_end.method_period)

    def test_compute_deferral_board_01(self):
        """
        Compute các dòng phần bổ với kiểu Number of Deferrals  và ngày vào sổ từ đầu tháng
            Input:
                Tạo phân bổ
                Entry Date: 01/01/2022
                Time Method: Number of Deferrals
                Number of Deferrals: 2
                Number of Months in a Period: 1
                Value: 20,000.00
                Salvage Value: 0.0
                Ấn 'compute'
            Output: ra 2 dòng phân bổ mỗi dòng phân bổ với số tiền 10,000
        """
        self.revenue_deferral.compute_deferral_board()
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'deferral_date': fields.Date.to_date('2022-01-01'),
                'distributed_value': 0.0,
                'amount': 10000.0,
                'remaining_value': 10000.0,
                'sequence': 1
            },
            {
                'deferral_date': fields.Date.to_date('2022-02-01'),
                'distributed_value': 10000.0,
                'amount': 10000.0,
                'remaining_value': 0.0,
                'sequence': 2
            }])

    def test_compute_deferral_board_02(self):
        """
        Tương tự test_compute_deferral_board_01 nhưng Entry Date: 15/01/2022
        """
        self.revenue_deferral.date = fields.Date.to_date('2022-01-15')

        self.revenue_deferral.compute_deferral_board()
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'deferral_date': fields.Date.to_date('2022-01-15'),
                'distributed_value': 0.0,
                'amount': 10000.0,
                'remaining_value': 10000.0,
                'sequence': 1
            },
            {
                'deferral_date': fields.Date.to_date('2022-02-15'),
                'distributed_value': 10000.0,
                'amount': 10000.0,
                'remaining_value': 0.0,
                'sequence': 2
            }])

    def test_compute_deferral_board_06(self):
        """
        Tương tự test_compute_deferral_board_01 nhưng Salvage Value là 10000
        """
        self.revenue_deferral.salvage_value = 10000.0

        self.revenue_deferral.compute_deferral_board()
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'deferral_date': fields.Date.to_date('2022-01-01'),
                'distributed_value': 0.0,
                'amount': 5000.0,
                'remaining_value': 5000.0,
                'sequence': 1
            },
            {
                'deferral_date': fields.Date.to_date('2022-02-01'),
                'distributed_value': 5000.0,
                'amount': 5000.0,
                'remaining_value': 0.0,
                'sequence': 2
            }])

    def test_compute_deferral_board_03(self):
        """
        Compute các dòng phần bổ với kiểu Ending Date  và ngày vào sổ từ đầu tháng
        Input:
            Tạo phân bổ
            Entry Date: 1/1/2022
            Time Method: Ending Date
            Ending Date: 31/3/2022
            Number of Months in a Period: 1
            Value: 20000
            Salvage Value: 0.0
            Ấn 'compute'
        Output: ra 3 dòng phân bổ mỗi dòng phân bổ với số tiền 6666.67
        """
        self.revenue_deferral.write({
            'method_time': 'end',
            'method_period': 1,
            'method_end': fields.Date.to_date('2022-03-31'),
        })
        self.revenue_deferral.compute_deferral_board()
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'deferral_date': fields.Date.to_date('2022-01-01'),
                'distributed_value': 0.0,
                'amount': 6666.67,
                'remaining_value': 13333.33,
                'sequence': 1
            },
            {
                'deferral_date': fields.Date.to_date('2022-02-01'),
                'distributed_value': 6666.67,
                'amount': 6666.67,
                'remaining_value': 6666.67,
                'sequence': 2
            },
            {
                'deferral_date': fields.Date.to_date('2022-03-01'),
                'distributed_value': 13333.33,
                'amount': 6666.67,
                'remaining_value': 0.0,
                'sequence': 3
            }])

    def test_compute_deferral_board_04(self):
        """
        Tương tự test_compute_deferral_board_03 nhưng Entry Date: 15/01/2022 và Ending Date: 15/3/2022
        """
        self.revenue_deferral.write({
            'date': fields.Date.to_date('2022-01-15'),
            'method_time': 'end',
            'method_period': 1,
            'method_end': fields.Date.to_date('2022-03-15'),
        })
        self.revenue_deferral.compute_deferral_board()
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'deferral_date': fields.Date.to_date('2022-01-15'),
                'distributed_value': 0.0,
                'amount': 6666.67,
                'remaining_value': 13333.33,
                'sequence': 1
            },
            {
                'deferral_date': fields.Date.to_date('2022-02-15'),
                'distributed_value': 6666.67,
                'amount': 6666.67,
                'remaining_value': 6666.67,
                'sequence': 2
            },
            {
                'deferral_date': fields.Date.to_date('2022-03-15'),
                'distributed_value': 13333.33,
                'amount': 6666.67,
                'remaining_value': 0.0,
                'sequence': 3
            }])

    def test_compute_deferral_board_05(self):
        """
        Tương tự test_compute_deferral_board_03 nhưng Entry Date: 15/01/2022 và Ending Date: 14/3/2022
        """
        self.revenue_deferral.write({
            'date': fields.Date.to_date('2022-01-15'),
            'method_time': 'end',
            'method_period': 1,
            'method_end': fields.Date.to_date('2022-03-14'),
        })
        self.revenue_deferral.compute_deferral_board()
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'deferral_date': fields.Date.to_date('2022-01-15'),
                'distributed_value': 0.0,
                'amount': 10000.0,
                'remaining_value': 10000.0,
                'sequence': 1
            },
            {
                'deferral_date': fields.Date.to_date('2022-02-15'),
                'distributed_value': 10000.0,
                'amount': 10000.0,
                'remaining_value': 0.0,
                'sequence': 2
            }])

    def test_compute_deferral_board_07(self):
        """
        Tương tự test_compute_deferral_board_03 nhưng Salvage Value là 2000
        """
        self.revenue_deferral.write({
            'method_time': 'end',
            'method_period': 1,
            'method_end': fields.Date.to_date('2022-03-31'),
            'salvage_value': 2000.0
        })

        self.revenue_deferral.compute_deferral_board()
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'deferral_date': fields.Date.to_date('2022-01-01'),
                'distributed_value': 0.0,
                'amount': 6000.0,
                'remaining_value': 12000.0,
                'sequence': 1
            },
            {
                'deferral_date': fields.Date.to_date('2022-02-01'),
                'distributed_value': 6000.0,
                'amount': 6000.0,
                'remaining_value': 6000.0,
                'sequence': 2
            },
            {
                'deferral_date': fields.Date.to_date('2022-03-01'),
                'distributed_value': 12000.0,
                'amount': 6000.0,
                'remaining_value': 0.0,
                'sequence': 3
            }])

    def test_compute_deferral_board_08(self):
        """
        Tương tự test_compute_deferral_board_03 nhưng Value là 0.0 => Residual Value = 0.0
        """
        self.revenue_deferral.value = 0.0
        self.revenue_deferral.compute_deferral_board()
        self.assertFalse(self.revenue_deferral.deferral_line_ids)

    def test_compute_deferral_board_09(self):
        """
        Tương tự test_compute_deferral_board_01 -> Xác nhận phân bổ -> đặt về dự thảo -> Sửa lại số tiền thành 30000
        => 2 dòng, mỗi dòng 15000
        """
        self.revenue_deferral.validate()
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'deferral_date': fields.Date.to_date('2022-01-01'),
                'distributed_value': 0.0,
                'amount': 10000.0,
                'remaining_value': 10000.0,
                'sequence': 1
            },
            {
                'deferral_date': fields.Date.to_date('2022-02-01'),
                'distributed_value': 10000.0,
                'amount': 10000.0,
                'remaining_value': 0.0,
                'sequence': 2
            }])
        self.revenue_deferral.set_to_draft()
        self.revenue_deferral.value = 30000.0
        self.revenue_deferral.validate()
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'deferral_date': fields.Date.to_date('2022-01-01'),
                'distributed_value': 0.0,
                'amount': 15000.0,
                'remaining_value': 15000.0,
                'sequence': 1
            },
            {
                'deferral_date': fields.Date.to_date('2022-02-01'),
                'distributed_value': 15000.0,
                'amount': 15000.0,
                'remaining_value': 0.0,
                'sequence': 2
            }])

    def test_actions_on_deferral(self):
        """
        Test buttons: Confirm, Set to Close
        """
        self.revenue_deferral.validate()
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'deferral_date': fields.Date.to_date('2022-01-01'),
                'distributed_value': 0.0,
                'amount': 10000.0,
                'remaining_value': 10000.0,
                'sequence': 1
            },
            {
                'deferral_date': fields.Date.to_date('2022-02-01'),
                'distributed_value': 10000.0,
                'amount': 10000.0,
                'remaining_value': 0.0,
                'sequence': 2
            }])
        self.assertEqual(self.revenue_deferral.state, 'open')

        self.revenue_deferral.set_to_close()
        self.assertEqual(self.revenue_deferral.state, 'close')

    def test_set_to_draft_01(self):
        """
        Xác nhận phân bổ -> Đặt về dự thảo
        => đặt về dự thảo thành công
        """
        self.revenue_deferral.validate()
        self.revenue_deferral.set_to_draft()
        self.assertEqual(self.revenue_deferral.state, 'draft')

    def test_set_to_draft_02(self):
        """
        Xác nhận phân bổ -> tạo 1 bút toán cho dòng phân bổ -> Đặt về dự thảo
        => đặt về dự thảo không thành công
        """
        self.revenue_deferral.validate()
        self.revenue_deferral.deferral_line_ids[0].create_move(post_move=False)
        self.assertRaises(UserError, self.revenue_deferral.set_to_draft)

    def test_set_to_draft_03(self):
        """
        Xác nhận phân bổ -> tạo 1 bút toán cho dòng phân bổ -> hủy bút toán -> Đặt về dự thảo
        => đặt về dự thảo thành công
        """
        self.revenue_deferral.validate()
        self.revenue_deferral.deferral_line_ids[0].create_move(post_move=False)
        self.revenue_deferral.deferral_line_ids[0].move_id.button_cancel()
        self.revenue_deferral.set_to_draft()
        self.assertEqual(self.revenue_deferral.state, 'draft')

    def test_unlink_deferral_lines_01(self):
        """
        Xóa dòng phân bổ chưa tham chiếu đến bút toán
        => Xóa thành công
        """
        self.revenue_deferral.validate()
        self.assertTrue(self.revenue_deferral.deferral_line_ids[0].unlink)
        self.cost_deferral.validate()
        self.assertTrue(self.cost_deferral.deferral_line_ids[0].unlink)

    def test_unlink_deferral_lines_02(self):
        """
        Xóa dòng phân bổ đã chiếu đến bút toán, trạng thái bút toán khác cancel
        => xóa không thành công
        """
        self.revenue_deferral.validate()
        self.revenue_deferral.deferral_line_ids[0].create_move(post_move=False)
        with self.assertRaises(UserError):
            self.revenue_deferral.deferral_line_ids[0].unlink()

        self.cost_deferral.validate()
        self.cost_deferral.deferral_line_ids[0].create_move(post_move=False)
        with self.assertRaises(UserError):
            self.cost_deferral.deferral_line_ids[0].unlink()

    def test_unlink_deferral_lines_03(self):
        """
        Xóa dòng phân bổ đã chiếu đến bút toán, trạng thái bút toán là cancel
        => Xóa thành công
        """
        self.revenue_deferral.validate()
        self.revenue_deferral.deferral_line_ids[0].create_move(post_move=False)
        self.revenue_deferral.deferral_line_ids[0].move_id.button_cancel()
        self.assertTrue(self.revenue_deferral.deferral_line_ids[0].unlink)

        self.cost_deferral.validate()
        self.cost_deferral.deferral_line_ids[0].create_move(post_move=False)
        self.cost_deferral.deferral_line_ids[0].move_id.button_cancel()
        self.assertTrue(self.cost_deferral.deferral_line_ids[0].unlink)

    def test_deferral_lines_by_account_move(self):
        """
        1. Dòng phân bổ => Tạo move => move_check = True
        2. Vào sổ bút toán của dòng phân bổ đấy => move_posted_check = True
        3. Hủy bút toán của dòng phân bổ đấy => move_posted_check = False
        """
        self.revenue_deferral.validate()
        self.revenue_deferral.deferral_line_ids[0].create_move(post_move=False)
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'move_check': True,
                'move_posted_check': False
            },
            {
                'move_check': False,
                'move_posted_check': False
            }])
        self.revenue_deferral.deferral_line_ids[0].move_id.action_post()
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'move_check': True,
                'move_posted_check': True
            },
            {
                'move_check': False,
                'move_posted_check': False
            }])
        self.revenue_deferral.deferral_line_ids[0].move_id.button_cancel()
        self.revenue_deferral.deferral_line_ids[1].create_move(post_move=False)
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'move_check': True,
                'move_posted_check': False
            },
            {
                'move_check': True,
                'move_posted_check': False
            }])

    def test_deferral_by_account_move(self):
        """
        Xác nhận phân bổ => Dòng phân bổ => Tạo move
        Residual Value được tính toán lại: trừ đi số tiền trên dòng phân bổ đã tạo bút toán và số tiền Salvage Value

        Vào sổ tất cả các bút toán => Trạng thái của phân bổ là Close
        """
        self.revenue_deferral.validate()
        self.assertRecordValues(
            self.revenue_deferral,
            [{
                'value_residual': 20000.0,
                'move_line_count': 0,
                'state': 'open'
            }])
        self.revenue_deferral.deferral_line_ids[0].create_move(post_move=False)
        self.assertRecordValues(
            self.revenue_deferral,
            [{
                'value_residual': 10000.0,
                'move_line_count': 2,
                'state': 'open'
            }])
        self.revenue_deferral.deferral_line_ids[1].create_move(post_move=False)
        self.assertRecordValues(
            self.revenue_deferral,
            [{
                'value_residual': 0.0,
                'move_line_count': 4,
                'state': 'open'
            }])

        self.revenue_deferral.deferral_line_ids.move_id.action_post()
        self.assertEqual(self.revenue_deferral.state, 'close')

    def test_check_type_consistent(self):
        self.assertRaises(ValidationError, self.revenue_deferral.write, {'type': 'cost'})

    def test_wizard_deferral_confirm(self):
        """
        Tạo tất cả các bút toán cho các dòng phân bổ nhỏ hơn ngày đã chọn
        - Điều kiện để tạo bút toán: trạng thái là 'open', chưa có bút toán, ngày phân bổ <= ngày được chọn

        Nếu phân bổ đánh dấu Auto-Posted Deferral => Vào sổ bút toán
        """
        self.revenue_deferral.validate()
        self.cost_deferral.auto_create_move = True
        self.cost_deferral.validate()
        wizard = self.env['deferral.confirm'].create({'date': fields.Date.to_date('2022-01-15')})
        wizard.deferral_compute()

        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'move_check': True,
                'move_posted_check': False
            },
            {
                'move_check': False,
                'move_posted_check': False
            }])
        self.assertRecordValues(
            self.cost_deferral.deferral_line_ids,
            [{
                'move_check': True,
                'move_posted_check': True
            },
            {
                'move_check': False,
                'move_posted_check': False
            }])

        wizard = self.env['deferral.confirm'].create({'date': fields.Date.to_date('2022-02-15')})
        wizard.deferral_compute()

        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'move_check': True,
                'move_posted_check': False
            },
            {
                'move_check': True,
                'move_posted_check': False
            }])
        self.assertRecordValues(
            self.cost_deferral.deferral_line_ids,
            [{
                'move_check': True,
                'move_posted_check': True
            },
            {
                'move_check': True,
                'move_posted_check': True
            }])

    def test_wizard_deferral_disposal_01(self):
        """
        Test exceptions
        """
        self.revenue_deferral.validate()
        wizard = self.env['deferral.disposal'].create({
            'date': fields.Date.to_date('2021-12-31'),
            'deferral_id': self.revenue_deferral.id,
            'name': 'Reason 1'
        })

        # 1.
        with self.assertRaises(ValidationError):
            wizard.action_disposal()

        #2.
        wizard.date = fields.Date.to_date('2022-01-15')
        with self.assertRaises(ValidationError):
            wizard.action_disposal()

        #3.
        self.revenue_deferral.deferral_line_ids[1].create_move(post_move=False)
        with self.assertRaises(ValidationError):
            wizard.action_disposal()

        # 4.
        wizard.date = fields.Date.to_date('2022-03-15')
        self.revenue_deferral.deferral_line_ids[0].create_move(post_move=False)
        self.assertFalse(self.revenue_deferral.deferral_line_ids.filtered(lambda r: not r.move_check))
        with self.assertRaises(ValidationError):
            wizard.action_disposal()

    def test_wizard_deferral_disposal_02(self):
        """
        Phân bổ số tiền 20000, có 4 dòng vào ngày 1 các tháng 1,2,3,4, mỗi dòng phân bổ có số tiền là 5000
        Tạo bút toán cho dòng phân bổ đầu tiên
        Thanh lý ngày 1/1/2022
        => Tạo 1 bút toán thanh lý phân bổ vơí số tiền 15000 và xóa dòng phân bổ tháng 2,3,4
        """
        self.revenue_deferral.method_number = 4
        self.revenue_deferral.validate()
        self.revenue_deferral.deferral_line_ids[0].create_move(post_move=False)
        wizard = self.env['deferral.disposal'].create({
            'date': fields.Date.to_date('2022-01-02'),
            'deferral_id': self.revenue_deferral.id,
            'name': 'Reason 1'
        })
        move = wizard.action_disposal()
        self.assertEqual(self.revenue_deferral.state, 'close')
        self.assertRecordValues(
            self.revenue_deferral.deferral_line_ids,
            [{
                'deferral_date': fields.Date.to_date('2022-01-01'),
                'move_check': True
            }])
        self.assertRecordValues(
            move,
            [{
                'date': fields.Date.to_date('2022-01-02'),
                'ref': 'RD',
                'journal_id': self.journal_revenue_deferral.id
            }])
        self.assertRecordValues(
            move.line_ids,
            [{
                'name': 'RD',
                'ref': 'RD',
                'account_id': self.account_unrealized_revenue.id, # category_id.deferred_account_id.id,
                'debit': 15000.0,
                'credit': 0.0,
                'journal_id': self.journal_revenue_deferral.id,
                'date': fields.Date.to_date('2022-01-02'),
                'deferral_id': self.revenue_deferral.id
            },
            {
                'name': 'RD',
                'ref': 'RD',
                'account_id': self.account_revenue.id, # category_id.recognition_account_id.id,
                'debit': 0.0,
                'credit': 15000.0,
                'journal_id': self.journal_revenue_deferral.id,
                'date': fields.Date.to_date('2022-01-02'),
                'deferral_id': self.revenue_deferral.id
            }])
