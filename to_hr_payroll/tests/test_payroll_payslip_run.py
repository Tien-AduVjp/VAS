from odoo import fields
from odoo.exceptions import ValidationError, UserError
from odoo.tests import tagged, Form
from .common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestPayrollPayslipRun(TestPayrollCommon):

    def create_payslip_run(self, name='', start=False, end=False):
        return self.env['hr.payslip.run'].create({
            'name': name or 'Test 1',
            'date_start': start or fields.Date.from_string('2021-7-1'),
            'date_end': end or fields.Date.from_string('2021-7-31'),
            'salary_cycle_id': self.env.company.salary_cycle_id.id
            })

    # 9. Bảng lương
    def test_salary_cycle_id(self):
        """
        Case 1:
            Input:
                Công ty có thiết lập chu kỳ lương
                Tạo bảng lương
            Output: chu kỳ lương mặc định được thiết lập trên công ty
        """
        f = Form(self.env['hr.payslip.run'])
        self.assertEqual(f.salary_cycle_id, self.env.company.salary_cycle_id, 'Test salary_cycle_id field not oke')

    # 9. Bảng lương
    def test_payslip_run_date(self):
        """
        Case 1: Tạo bảng lương với Ngày bắt đầu phải nhỏ hơn ngày kết thúc
            TH1: Ngày bắt đầu < ngày kết thúc
                => Tạo thành công
            TH2: Ngày bắt đầu > ngày kết thúc
                => Tạo không thành công
        """
        PayslipRun = self.env['hr.payslip.run']

        # TH1: Ngày bắt đầu < ngày kết thúc
        result1 = PayslipRun.create({
            'name': 'Test 1',
            'date_start': fields.Date.from_string('2021-7-1'),
            'date_end': fields.Date.from_string('2021-7-31'),
            'salary_cycle_id': self.env.company.salary_cycle_id.id,
        })
        self.assertTrue(result1, 'Test Payslip Batch: date_start < date_end not oke')

        # TH2: Ngày bắt đầu > ngày kết thúc
        vals = {
            'name': 'Test 2',
            'date_start': fields.Date.from_string('2021-9-1'),
            'date_end': fields.Date.from_string('2021-8-8'),
            'salary_cycle_id': self.env.company.salary_cycle_id.id
        }
        self.assertRaises(ValidationError, PayslipRun.create, vals)

    # 9. Bảng lương
    def test_generate_payslip_1(self):
        """
        Case 2: Tạo nhanh phiếu lương cho nhiều người, chế độ chu kỳ bảng lương
        Output:
            Tạo thành công các phiếu lương và được tham chiếu đến bảng lương này
            Các phiếu lương là các phiếu lương có hợp đồng, thời gian hợp lệ với khoảng thời gian trên bảng lương.
            khoảng thời gian trên phiếu lương giống với khoảng thời gian của bảng lương
        """
        # Prepare data
        # manager's contract
        self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-1-1'),
            fields.Date.from_string('2021-7-15'))
        # new employee
        employee_3 = self.create_employee('Project Employee 1')
        employees = self.env['hr.employee'].search([('company_id', '=', self.env.company.id)])

        # batch_1: 1/7/2021 -> 31/7/2021
        batch_1 = self.create_payslip_run()
        # Create wizard
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch_1.id,
            'mode': 'batch_period',
            'employee_ids': [(6,0, employees.ids)]
        })
        # Generate Payslips
        wizard.compute_sheet()

        # Test
        payslip_1 = batch_1.slip_ids.filtered(lambda r:r.employee_id == self.product_emp_A)
        self.assertTrue(payslip_1, 'Test Generate Payslips not oke')
        self.assertEqual(payslip_1.date_from, fields.Date.from_string('2021-7-1'), 'Test Generate Payslips not oke')
        self.assertEqual(payslip_1.date_to, fields.Date.from_string('2021-7-31'), 'Test Generate Payslips not oke')
        self.assertEqual(payslip_1.state, 'draft', 'Test Generate Payslips not oke')

        payslip_2 = batch_1.slip_ids.filtered(lambda r:r.employee_id == self.product_dep_manager)
        self.assertTrue(payslip_2, 'Test Generate Payslips not oke')
        self.assertEqual(payslip_2.date_from, fields.Date.from_string('2021-7-1'), 'Test Generate Payslips not oke')
        self.assertEqual(payslip_2.date_to, fields.Date.from_string('2021-7-31'), 'Test Generate Payslips not oke')
        self.assertEqual(payslip_2.state, 'draft', 'Test Generate Payslips not oke')

        payslip_3 = batch_1.slip_ids.filtered(lambda r:r.employee_id == employee_3)
        self.assertFalse(payslip_3, 'Test Generate Payslips not oke')

    # 9. Bảng lương
    def test_generate_payslip_2(self):
        """
        Case 3: Tạo nhanh phiếu lương cho nhiều người, chế độ thời hạn hợp đồng
        Output:
            Tạo thành công các phiếu lương và được tham chiếu đến bảng lương này
            Các phiếu lương là các phiếu lương có hợp đồng, thời gian hợp lệ với khoảng thời gian trên bảng lương.
            Thời gian kết thúc của phiếu lương được tính dựa theo thời gian kết thúc của hợp đồng,
                nếu thời gian kết thúc trên bảng lương > thời gian kết thúc hợp đồng
                    => thời gian kết thúc phiếu lương là thời gian kết thúc hợp đồng
        """
        # Prepare data
        # manager's contract
        self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-1-1'),
            fields.Date.from_string('2021-7-15'),
            'open')
        # new employee
        employee_3 = self.create_employee('Project Employee 1')
        employees = self.env['hr.employee'].search([('company_id', '=', self.env.company.id)])

        # batch_1: 1/7/2021 -> 31/7/2021
        batch_1 = self.create_payslip_run()
        # Create wizard
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch_1.id,
            'mode': 'contract_period',
            'employee_ids': [(6,0, employees.ids)]
        })
        # Generate Payslips
        wizard.compute_sheet()

        # Test
        payslip_1 = batch_1.slip_ids.filtered(lambda r:r.employee_id == self.product_emp_A)
        self.assertTrue(payslip_1, 'Test Generate Payslips not oke')
        self.assertEqual(payslip_1.date_from, fields.Date.from_string('2021-7-1'), 'Test Generate Payslips not oke')
        self.assertEqual(payslip_1.date_to, fields.Date.from_string('2021-7-31'), 'Test Generate Payslips not oke')
        self.assertEqual(payslip_1.state, 'draft', 'Test Generate Payslips not oke')

        payslip_2 = batch_1.slip_ids.filtered(lambda r:r.employee_id == self.product_dep_manager)
        self.assertTrue(payslip_2, 'Test Generate Payslips not oke')
        self.assertEqual(payslip_2.date_from, fields.Date.from_string('2021-7-1'), 'Test Generate Payslips not oke')
        self.assertEqual(payslip_2.date_to, fields.Date.from_string('2021-7-15'), 'Test Generate Payslips not oke')
        self.assertEqual(payslip_2.state, 'draft', 'Test Generate Payslips not oke')

        payslip_3 = batch_1.slip_ids.filtered(lambda r:r.employee_id == employee_3)
        self.assertFalse(payslip_3, 'Test Generate Payslips not oke')

    # 9. Bảng lương
    def test_payslip_run_duplicate(self):
        """
        Case 13: Test bảng lương không thể nhân bản
            Input: nhân bản bảng lương
            Output: Thông báo ngoại lệ
        """
        batch_1 = self.create_payslip_run()
        self.assertRaises(UserError, batch_1.copy)

    # 9. Bảng lương
    def test_payslip_run_unlink_1(self):
        """
        Case 12 : Test xóa bảng lương
            TH1: bảng lương k có phiếu lương nào, tất cả trạng thái đều xóa đc
                Output: Xóa thành công
        """
        # draft
        batch_1 = self.create_payslip_run()
        self.assertTrue(batch_1.unlink(), 'Test Unlink: Payslip Batch not oke')

        # Verified
        batch_2 = self.create_payslip_run()
        batch_2.action_verify_payslips()
        self.assertTrue(batch_2.unlink(), 'Test Unlink: Payslip Batch not oke')

        # Close
        batch_3 = self.create_payslip_run()
        batch_3.close_payslip_run()
        self.assertTrue(batch_3.unlink(), 'Test Unlink: Payslip Batch not oke')

        # Cancel
        batch_4 = self.create_payslip_run()
        batch_4.action_cancel()
        self.assertTrue(batch_4.unlink(), 'Test Unlink: Payslip Batch not oke')

    # 9. Bảng lương
    def test_payslip_run_unlink_2(self):
        """
        Case 12 : Test xóa bảng lương
            TH2: Bảng lương có phiếu lương và ở trạng thái bảng lương khác dự thảo
                Output: Xóa không thành công
        """
        batch_1 = self.create_payslip_run()
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch_1.id,
            'mode': 'batch_period',
            'employee_ids': [(6,0, self.product_emp_A.ids)]
            })
        # Generate Payslips
        wizard.compute_sheet()

        batch_1.action_verify_payslips()
        self.assertRaises(UserError, batch_1.unlink)

    # 9. Bảng lương
    def test_payslip_run_unlink_3(self):
        """
        Case 12 : Test xóa bảng lương
            TH3: Bảng lương có phiếu lương và ở trạng thái dự thảo, có phiếu lương ở trạng thái "dự thảo"
                Output: Xóa thành công bảng lương và các phiếu lương
        """
        batch_1 = self.create_payslip_run()
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch_1.id,
            'mode': 'batch_period',
            'employee_ids': [(6,0, self.product_emp_A.ids)]
            })
        # Generate Payslips
        wizard.compute_sheet()

        self.assertTrue(batch_1.unlink(), 'Test Unlink: Payslip Batch not oke')
        self.assertFalse(batch_1.slip_ids.exists(), 'Test Unlink: Payslip Batch not oke')

    # 9. Bảng lương
    def test_payslip_run_unlink_6(self):
        """
        Case 12 : Test xóa bảng lương
            TH6: Bảng lương có phiếu lương và ở trạng thái dự thảo, có phiếu lương ở trạng thái "hủy"
                Output: Xóa thành công bảng lương và các phiếu lương
        """
        batch_1 = self.create_payslip_run()
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch_1.id,
            'mode': 'batch_period',
            'employee_ids': [(6,0, self.product_emp_A.ids)]
            })
        # Generate Payslips
        wizard.compute_sheet()

        batch_1.slip_ids.action_payslip_cancel()
        self.assertTrue(batch_1.unlink(), 'Test Unlink: Payslip Batch not oke')
        self.assertFalse(batch_1.slip_ids.exists(), 'Test Unlink: Payslip Batch not oke')

    # 9. Bảng lương
    def test_payslip_run_unlink_45(self):
        """
        Case 12 : Test xóa bảng lương
            TH4: Bảng lương có phiếu lương và ở trạng thái dự thảo, có phiếu lương ở trạng thái "chờ đợi"
                Output: Xóa không thành công
            TH5: Bảng lương có phiếu lương và ở trạng thái dự thảo, có phiếu lương ở trạng thái "hoàn thành"
                Output: Xóa không thành công
        """
        batch_1 = self.create_payslip_run()
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch_1.id,
            'mode': 'batch_period',
            'employee_ids': [(6,0, self.product_emp_A.ids)]
            })
        # Generate Payslips
        wizard.compute_sheet()

        # TH4
        batch_1.slip_ids.action_payslip_verify()
        self.assertRaises(UserError, batch_1.unlink)
        # TH5
        batch_1.slip_ids.action_payslip_done()
        self.assertRaises(UserError, batch_1.unlink)

    # 9. Bảng lương
    def test_payslip_run_action_compute_sheets(self):
        """
        Case 8: Test hành động tính toán hàng loạt phiếu lương (Compute Payslip Batch)
            TH2: Bảng lương ở trạng thái Dự thảo, các phiếu lương ở trạng thái dự thảo
                Ouput: Xuất hiện nút tính toán bảng lương (Compute Payslip Batch), khi nhấn vào sẽ tính toán toàn bộ các phiếu lương

            TH1: Bảng lương ở trạng thái Dự thảo, có bất kỳ phiếu 1 ương khác trạng thái dự thảo
                Ouput: Xuất hiện nút tính toán bảng lương (Compute Payslip Batch), khi nhấn vào sẽ thông báo ngoại lệ
        """
        batch_1 = self.create_payslip_run()
        # TH2: payslip_1: draft
        payslip_1 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-10'),
            self.contract_open_emp_A.id)
        payslip_1.write({'payslip_run_id': batch_1.id})
        batch_1.action_compute_sheets()

        # TH1: payslip_2: cancel
        payslip_1.action_payslip_cancel()
        self.assertRaises(UserError, batch_1.action_compute_sheets)

    # 9. Bảng lương
    def test_payslip_run_action_close(self):
        """
        Case 9: Test hành động đóng bảng lương
            => Trạng thái của bảng lương là "Đóng"
        """
        batch_1 = self.create_payslip_run()
        batch_1.close_payslip_run()
        self.assertEqual(batch_1.state, 'close', 'Test action: close_payslip_run() not oke')

    def test_payslip_run_action_verify(self):
        """
        Case 10A: Xác nhận trạng thái phiếu lương khi xác nhận bảng lương
            Input: Xác nhận bảng lương
            Output:
                Tất cả phiếu lương trong bảng lương ở trạng thái dự thảo chuyển sang trạng thái Đang đợi
                Các phiếu lương ở trạng thái khác dự thảo không thay đổi trạng thái
        """
        # 3 employees - 3 contracts
            # self.product_emp_A.id
            # self.product_dep_manager.id
            # employee_3
        employee_3 = self.create_employee('Product Employee 3')
        self.create_contract(employee_3.id, fields.Date.from_string('2021-1-1'))
        self.create_contract(self.product_dep_manager.id, fields.Date.from_string('2021-1-1'))

        # salary batch
        batch_1 = self.create_payslip_run()
        # Create wizard with 3 employees
        employees_ids = [self.product_emp_A.id, self.product_dep_manager.id, employee_3.id]
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch_1.id,
            'mode': 'batch_period',
            'employee_ids': [(6,0, employees_ids)]
            })
        # Generate Payslips
        wizard.compute_sheet()

        # payslip_2: cancel
        batch_1.slip_ids[1].action_payslip_verify()
        batch_1.slip_ids[1].action_payslip_cancel()

        # payslip_3: done
        batch_1.slip_ids[2].action_payslip_verify()
        batch_1.slip_ids[2].action_payslip_done()

        # payslip_1: draft
        # Xác nhận bảng lương
        batch_1.action_verify_payslips()

        self.assertEqual(batch_1.state, 'verified', 'Test action_payslip_verify() on payslip batch not oke')
        self.assertEqual(batch_1.slip_ids[0].state, 'verify', 'Test action_payslip_verify() on payslip batch not oke')
        self.assertEqual(batch_1.slip_ids[1].state, 'cancel', 'Test action_payslip_verify() on payslip batch not oke')
        self.assertEqual(batch_1.slip_ids[2].state, 'done', 'Test action_payslip_verify() on payslip batch not oke')

    def test_payslip_run_action_cancel(self):
        """
        Case 10B: Xác nhận trạng thái phiếu lương khi hủy bảng lương
            Input: Hủy bảng lương
            Output: Tất cả phiếu lương trong bảng lương chuyển sang trạng thái Bị từ chối
        """
        batch_1 = self.create_payslip_run()
        # payslip_1: draft
        payslip_1 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-10'),
            self.contract_open_emp_A.id)

        # payslip_2: verify
        payslip_2 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-11'),
            fields.Date.from_string('2021-7-20'),
            self.contract_open_emp_A.id)
        payslip_2.action_payslip_verify()

        # payslip_3: done
        payslip_3 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-21'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        payslip_3.action_payslip_verify()
        payslip_3.action_payslip_done()

        batch_1.write({'slip_ids': [(6,0, [payslip_1.id, payslip_2.id, payslip_3.id])]})
        batch_1.action_cancel()

        self.assertEqual(batch_1.state, 'cancelled', 'Test action_cancel() on payslip batch not oke')
        self.assertEqual(payslip_1.state, 'cancel', 'Test action_cancel() on payslip batch not oke')
        self.assertEqual(payslip_2.state, 'cancel', 'Test action_cancel() on payslip batch not oke')
        self.assertEqual(payslip_3.state, 'cancel', 'Test action_cancel() on payslip batch not oke')

    def test_compute_count_1(self):
        """
        Nhân viên A có 1 hợp đồng trong tháng 7
        Tạo bảng lương tháng 7 và có 1 phiếu lương của nhân viên A

        Output:
        Số lượng hợp đồng là 1
        Số lượng nhân viên là 1
        Số lượng phiếu lương là 1

        """
        # batch_1: 1/7/2021 -> 31/7/2021
        batch_1 = self.create_payslip_run()
        # Create wizard
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch_1.id,
            'mode': 'batch_period',
            'employee_ids': [(6,0, self.product_emp_A.ids)]
        })
        # Generate Payslips
        wizard.compute_sheet()

        self.assertRecordValues(
            batch_1,
            [{
                'employees_count': 1,
                'payslips_count': 1,
                'contracts_count': 1
            }])

    def test_compute_count_2(self):
        """
        Nhân viên A có 2 hợp đồng trong tháng 7
        Tạo bảng lương tháng 7 và có 1 phiếu lương của nhân viên A

        Output:
        Số lượng hợp đồng là 2
        Số lượng nhân viên là 1
        Số lượng phiếu lương là 1
        """
        self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-15'),
            'open')
        self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-16'),
            fields.Date.from_string('2021-7-31'),
            'open')
        # batch_1: 1/7/2021 -> 31/7/2021
        batch_1 = self.create_payslip_run()
        # Create wizard
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch_1.id,
            'mode': 'batch_period',
            'employee_ids': [(6,0, self.product_dep_manager.ids)]
        })
        # Generate Payslips
        wizard.compute_sheet()

        self.assertRecordValues(
            batch_1,
            [{
                'employees_count': 1,
                'payslips_count': 1,
                'contracts_count': 2
            }])

    def test_compute_count_3(self):
        """
        Tạo bảng lương tháng 7 và có 2 phiếu lương của 2 nhân viên

        Output:
        Số lượng hợp đồng là 2
        Số lượng nhân viên là 2
        Số lượng phiếu lương là 2
        """
        self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            'open')
        # batch_1: 1/7/2021 -> 31/7/2021
        batch_1 = self.create_payslip_run()
        # Create wizard
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch_1.id,
            'mode': 'batch_period',
            'employee_ids': [(6,0, (self.product_emp_A + self.product_dep_manager).ids)]
        })
        # Generate Payslips
        wizard.compute_sheet()

        self.assertRecordValues(
            batch_1,
            [{
                'employees_count': 2,
                'payslips_count': 2,
                'contracts_count': 2
            }])

    def test_compute_count_4(self):
        """
        Tạo bảng lương tháng 7 và có 2 phiếu lương của 2 nhân viên
        Nhân viên 1 có 2 hợp đồng trong tháng 7
        Nhân viên 2 có 1 hợp đồng trong tháng 7

        Output:
        Số lượng hợp đồng là 3
        Số lượng nhân viên là 2
        Số lượng phiếu lương là 2
        """
        self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-15'),
            'open')
        self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-16'),
            fields.Date.from_string('2021-7-31'),
            'open')
        # batch_1: 1/7/2021 -> 31/7/2021
        batch_1 = self.create_payslip_run()
        # Create wizard
        wizard = self.env['hr.payslip.employees'].create({
            'batch_id': batch_1.id,
            'mode': 'batch_period',
            'employee_ids': [(6,0, (self.product_emp_A + self.product_dep_manager).ids)]
        })
        # Generate Payslips
        wizard.compute_sheet()

        self.assertRecordValues(
            batch_1,
            [{
                'employees_count': 2,
                'payslips_count': 2,
                'contracts_count': 3
            }])

    def test_compute_count_5(self):
        """
        Nhân viên 1 có 2 hợp đồng trong tháng 7, từ 1/7 đến 15/7 và 16/7 đến
        Nhân viên 2 có 1 hợp đồng trong tháng 7
        Tạo bảng lương tháng 7 và có 3 phiếu lương của 2 nhân viên
        Phiếu lương 1: Nhân viên 1, từ 1/7 đến 20/7
        Phiếu lương 2: Nhân viên 1, từ 21/7 đến 31/7
        Phiếu lương 3: Nhân viên 2, từ 1/7 đến 31/7

        Output:
        Số lượng hợp đồng là 3
        Số lượng nhân viên là 2
        Số lượng phiếu lương là 3
        """
        contract_1 = self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-15'),
            'open')
        contract_2 = self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-16'),
            fields.Date.from_string('2021-7-31'),
            'open')

        # batch_1: 1/7/2021 -> 31/7/2021
        batch_1 = self.create_payslip_run()

        # payslip 1: 1/7/2021 -> 20/7/2021
        payslip_1 = self.create_payslip(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-20'),
            contract_1.id)
        # payslip 2: 21/7/2021 -> 31/7/2021
        payslip_2 = self.create_payslip(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-21'),
            fields.Date.from_string('2021-7-31'),
            contract_2.id)
        # payslip 3: 1/7/2021 -> 31/7/2021
        payslip_3 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)

        batch_1.write({
            'slip_ids': [(6,0,(payslip_1 | payslip_2 | payslip_3).ids)]
        })
        self.assertRecordValues(
            batch_1,
            [{
                'employees_count': 2,
                'payslips_count': 3,
                'contracts_count': 3
            }])

    # 8. Phiếu lương
    def test_thirteen_month_pay_year_1(self):
        """
        Tạo bảng lương tháng 13 với năm < 1970 hoặc năm >= 9999

        => Tạo không thành công
        """
        with self.assertRaises(UserError):
            self.env['hr.payslip.run'].with_context(tracking_disable=True).create({
                'name': 'Test 1',
                'date_start': fields.Date.from_string('2021-1-1'),
                'date_end': fields.Date.from_string('2021-1-31'),
                'salary_cycle_id': self.env.company.salary_cycle_id.id,
                'thirteen_month_pay': True,
                'thirteen_month_pay_year': 9999,
            })
        with self.assertRaises(UserError):
            self.env['hr.payslip.run'].with_context(tracking_disable=True).create({
                'name': 'Test 1',
                'date_start': fields.Date.from_string('2021-1-1'),
                'date_end': fields.Date.from_string('2021-1-31'),
                'salary_cycle_id': self.env.company.salary_cycle_id.id,
                'thirteen_month_pay': True,
                'thirteen_month_pay_year': 1969,
            })

    # 8. Phiếu lương
    def test_thirteen_month_pay_year_2(self):
        """
        Sửa bảng lương tháng 13 với năm < 1970 hoặc năm >= 9999

        => Thông báo ngoại lệ
        """
        batch = self.env['hr.payslip.run'].with_context(tracking_disable=True).create({
            'name': 'Test 1',
            'date_start': fields.Date.from_string('2021-1-1'),
            'date_end': fields.Date.from_string('2021-1-31'),
            'salary_cycle_id': self.env.company.salary_cycle_id.id,
            'thirteen_month_pay': True,
            'thirteen_month_pay_year': 2021,
        })

        with self.assertRaises(UserError):
            batch.write({
                'thirteen_month_pay_year': 1969
            })
        with self.assertRaises(UserError):
            batch.write({
                'thirteen_month_pay_year': 9999
            })
