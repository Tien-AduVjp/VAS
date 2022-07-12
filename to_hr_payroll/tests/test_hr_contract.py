from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged, Form

from .common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestHRContract(TestPayrollCommon):
    
    # 2. Form Hợp đồng
    def test_form_contract_onchange_job_id_1(self):
        """
        Case 1: Test thay đổi Chức vụ trên Hợp đồng lao động
            TH 2: Hợp đồng ở trạng thái dự thảo và Thay đổi chức vụ trên hợp đồng
                Output: Cấu trúc lương, lịch làm việc, lương cơ bản thay đổi giống với trên Chức vụ đã chọn
        """
        job = self.job_product_dev
        struct = self.structure_base.copy()
        job.write({
            'struct_id': struct.id,
            'resource_calendar_id': self.env.ref('resource.resource_calendar_std_38h').id
        })
         
        with Form(self.contract_draft_emp_A) as f:
            f.job_id = job
            self.assertEqual(f.struct_id, job.struct_id, 'Test onchange _onchange_job_id not oke')
            self.assertEqual(f.resource_calendar_id, job.resource_calendar_id, 'Test onchange _onchange_job_id not oke')
            self.assertEqual(f.wage, job.wage, 'Test onchange _onchange_job_id not oke')
     
    # 2. Form Hợp đồng
    def test_form_contract_onchange_job_id_2(self):
        """
        Case 1: Test thay đổi Chức vụ trên Hợp đồng lao động
            TH 1: Hợp đồng khác trạng thái Dự thảo
                Ouput: Không thể chỉnh sửa trường Chức vụ, cấu trúc lương,..
        """
        # 3 contracts: open, close, cancel
        for contract in [self.contract_open_emp_A, self.contract_cancel_emp_A, self.contract_close_emp_A]:
            with Form(contract) as f:
                self.assertTrue(f._get_modifier('job_id', 'readonly'), 'Test Job Position field is readonly not oke')
                self.assertTrue(f._get_modifier('struct_id', 'readonly'), 'Test Salary Structure field is readonly not oke')
     
    # 2. Form Hợp đồng
    def test_form_contract_grosss_salary(self):
        """
        Case 2: Test tính toán "Lương tổng" khi thay đổi "Lương cơ bản", "Phúc lợi hàng tháng"
            Output: Lương tổng được tính toán lại: Lương tổng = Lương cơ bản + tổng số tiền "Phúc lợi hàng tháng"
        """
        advantages = self.env['hr.advantage.template'].search([('company_id', '=', self.env.company.id)])
        with Form(self.contract_draft_emp_A) as f:
            f.wage = 5000
            self.assertEqual(5000, f.gross_salary, 'Test compute _compute_gross_sal not oke')
            with f.advantage_ids.new() as line:
                line.template_id = advantages[0]
                line.amount = 100
            with f.advantage_ids.new() as line:
                line.template_id = advantages[1]
                line.amount = 200
            # 5000 + 100 +200
            self.assertEqual(5300, f.gross_salary, 'Test compute _compute_gross_sal not oke')
             
            # 6000 + 100 +200
            f.wage = 6000
            self.assertEqual(6300, f.gross_salary, 'Test compute _compute_gross_sal not oke')
             
            # 6000 +300 +200
            with f.advantage_ids.edit(0) as line:
                line.amount = 300
            self.assertEqual(6500, f.gross_salary, 'Test compute _compute_gross_sal not oke')
             
            # 6000 + 300 + 100
            with f.advantage_ids.edit(1) as line:
                line.amount = 100
            self.assertEqual(6400, f.gross_salary, 'Test compute _compute_gross_sal not oke')
     
    # 2. Form Hợp đồng
    def test_form_contract_payslips_auto_generation(self):
        """
        Case 3: Test tính trường "Tự động tạo phiếu lương" khi tạo hợp đồng
            Output:  trường "Tự động tạo phiếu lương" được thiết lập mặc định trong phần Payroll Setting , và có thể thay đổi
        """
        f = Form(self.env['hr.contract'])
        self.assertFalse(f.payslips_auto_generation, 'Test default field: payslips_auto_generation not oke')
         
        self.env.company.write({'payslips_auto_generation': True})
        f = Form(self.env['hr.contract'])
        self.assertTrue(f.payslips_auto_generation, 'Test default field: payslips_auto_generation not oke')
     
    # 2. Form Hợp đồng
    def test_form_contract_tax_rule_12(self):
        """
        Case 4: Test Trường "Quy tắc thuế" được thiết lập mặc định
            TH1: Không có quy tắc thuế theo chính sách thuế 
                => Để trống
            TH2: Không có quy tắc thuế nào theo quốc gia của công ty 
                => Để trống
        """
        TaxRule = self.env['personal.tax.rule']
        tax_rules = TaxRule.search([])
        tax_rules.write({'personal_tax_policy': 'flat_rate'})
         
        # TH1:
        f = Form(self.env['hr.contract'], view="hr_contract.hr_contract_view_form")
        f.employee_id = self.product_emp_A
        f.personal_tax_policy = 'escalation'
        self.assertFalse(f.personal_tax_rule_id, 'Test compute _get_tax_rule not oke')
         
        # TH2:
        tax_rules.write({
            'country_id': self.env.ref('base.dz').id
        })
        TaxRule = self.env['personal.tax.rule']
        f = Form(self.env['hr.contract'], view="hr_contract.hr_contract_view_form")
        f.employee_id = self.product_emp_A
        f.personal_tax_policy = 'escalation'
        self.assertFalse(f.personal_tax_rule_id, 'Test compute _compute_gross_sal not oke')
        f.personal_tax_policy = 'flat_rate'
        self.assertFalse(f.personal_tax_rule_id, 'Test compute _compute_gross_sal not oke')
         
    # 2. Form Hợp đồng
    def test_form_contract_tax_rule_3(self):
        """
        Case 4: Test Trường "Quy tắc thuế" được thiết lập mặc định
            TH3: Có từ 1 đến nhiều quy tắc thuế: mặc định quy tắc thuế đầu tiên theo thứ tự ưu tiên
        """
        TaxRule = self.env['personal.tax.rule']
        TaxRule.create({'country_id': self.product_emp_A.address_home_id.country_id.id, 'sequence': 3})
        tax2 = TaxRule.create({'country_id': self.product_emp_A.address_home_id.country_id.id, 'sequence':-999})
        TaxRule.search([]).write({'personal_tax_policy': 'flat_rate'})
         
        f = Form(self.env['hr.contract'], view="hr_contract.hr_contract_view_form")
        f.employee_id = self.product_emp_A
        f.personal_tax_policy = 'flat_rate'
        self.assertEqual(f.personal_tax_rule_id, tax2, 'Test compute _get_tax_rule not oke')
     
    # 3. Hợp đồng: hr.contract
    def test_contract_contribution_register_1(self):
        """
        Case 1: Test hành động "Generate Payroll Contribution Registers" trong tab "Contribution Registers" 
            TH1: Hợp đồng không có kiểu đóng góp từ lương nào
                => không tạo đăng ký đóng góp từ lương
        """
        contract = self.contract_open_emp_A
        contract.generate_payroll_contribution_registers()
        self.assertFalse(contract.payroll_contribution_register_ids, 'Test method: generate_payroll_contribution_registers not oke')
     
    # 3. Hợp đồng: hr.contract
    def test_contract_contribution_register_2(self):
        """
        Case 1: Test hành động "Generate Payroll Contribution Registers" trong tab "Contribution Registers" 
            TH2. Hợp đồng có kiểu đóng góp, nhưng chưa có đăng ký đóng góp liên quan đến kiểu đóng góp đã chọn
                => Tạo ra các đăng ký đóng góp liên quan đến kiểu đóng góp ở trạng thái dự thảo
        """
        contract = self.contract_open_emp_A
        contribution_types = self.env['hr.payroll.contribution.type'].search([('company_id', '=', self.env.company.id)])
        contract.write({'payroll_contribution_type_ids': [(6, 0, contribution_types.ids)]})
         
        contract.generate_payroll_contribution_registers()
         
        self.assertEqual(
            contract.payroll_contribution_type_ids,
            contract.payroll_contribution_register_ids.type_id,
            'Test method: generate_payroll_contribution_registers not oke')
         
        state = set(contract.payroll_contribution_register_ids.mapped('state'))
        self.assertEqual({'draft'}, state, 'Test method: generate_payroll_contribution_registers not oke')
     
    # 3. Hợp đồng: hr.contract
    def test_contract_contribution_register_3(self):
        """
        Case 1: Test hành động "Generate Payroll Contribution Registers" trong tab "Contribution Registers" 
            TH3: Hợp đồng có kiểu đóng góp, đã có đắng ký đóng góp liên quan đến kiểu đóng góp
            Output: 
                những đăng ký đóng góp cũ liên quan đến kiểu đóng góp giữ nguyên, 
                những kiểu đăng ký đóng góp chưa có đăng ký đóng góp sẽ tạo mới
        """
        contract = self.contract_open_emp_A
        contribution_types = self.env['hr.payroll.contribution.type'].search([('company_id', '=', self.env.company.id)])
        contract.write({'payroll_contribution_type_ids': [(6, 0, contribution_types[1].ids)]})
         
        contract.generate_payroll_contribution_registers()
        contract.payroll_contribution_register_ids.action_confirm()
         
        # old data
        old_register_ids = contract.payroll_contribution_register_ids
        old_record_state = set(old_register_ids.mapped('state'))
         
        contract.write({'payroll_contribution_type_ids': [(6, 0, contribution_types.ids)]})
        contract.generate_payroll_contribution_registers()
         
        # new data
        new_register_ids = contract.payroll_contribution_register_ids
        new_record_state = set((new_register_ids - old_register_ids).mapped('state'))
         
        self.assertEqual(
            contract.payroll_contribution_type_ids,
            contract.payroll_contribution_register_ids.type_id,
            'Test method: generate_payroll_contribution_registers not oke')
         
        self.assertEqual({'draft'}, new_record_state, 'Test method: generate_payroll_contribution_registers not oke')
        self.assertEqual({'confirmed'}, old_record_state, 'Test method: generate_payroll_contribution_registers not oke')
     
    # 2. Form Hợp đồng:
    def test_contract_payslip_count(self):
        """
        Case 6: Test tính toán Số lượng phiếu lương trên hợp đồng
        """
        self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-07-01'),
            fields.Date.from_string('2021-07-30'),
            self.contract_open_emp_A.id)
        self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-06-01'),
            fields.Date.from_string('2021-06-30'),
            self.contract_open_emp_A.id)
        self.contract_open_emp_A.flush()
        self.assertEqual(2, self.contract_open_emp_A.payslips_count, 'Test payslip count not oke')
     
    # 3. Hợp đồng: hr.contract
    def test_contract_unlink_with_payslips_1(self):
        """
        Case 2: Test Xóa Hợp đồng
            TH1: Hợp đồng không liên quan đến phiếu lương nào
                Ouput: Xóa hợp đồng thành công
        """
        self.assertTrue(self.contract_cancel_emp_A.unlink)
    
    # 3. Hợp đồng: hr.contract
    def test_contract_unlink_with_payslips_2(self):
        """
        Case 2: Test Xóa Hợp đồng
            TH2: Hợp đồng có liên quan đến phiếu lương
                Ouput: Xóa hợp đồng không thành công
        """
        payslip1 = self.create_payslip(self.product_emp_A.id,
                            fields.Date.from_string('2021-07-01'),
                            fields.Date.from_string('2021-07-30'),
                            self.contract_open_emp_A.id)
        
        # use flush to update the relationship between payslip and contract
        payslip1.flush()
        self.contract_open_emp_A.write({'state': 'cancel'})
        with self.assertRaises(UserError):
            self.contract_open_emp_A.unlink()

    # 3. Hợp đồng: hr.contract
    def test_compute_included_contribution_register(self):
        """
        Mẫu phụ cấp TRAVEL cho hợp đồng có đánh dấu là `bao gồm trong đăng ký đóng góp từ lương`
        Mẫu phụ cấp PHONE cho hợp đồng không đánh dấu là `bao gồm trong đăng ký đóng góp từ lương`
        Mẫu phụ cấp MEAL cho hợp đồng không đánh dấu là `bao gồm trong đăng ký đóng góp từ lương`
        Trên hợp đồng, chọn mẫu đãi ngộ có mẫu phụ cấp: TRAVEL, PHONE, MEAL
        * với đãi ngộ MEAL, đánh dấu `bao gồm trong đăng ký đóng góp từ lương` trên hợp đồng
        
        Output:
            Dòng đãi ngộ của hợp đồng (TRAVEL), Trường `bao gồm trong đăng ký đóng góp từ lương` là True
            Dòng đãi ngộ của hợp đồng (PHONE), Trường `bao gồm trong đăng ký đóng góp từ lương` là False
            Dòng đãi ngộ của hợp đồng (MEAL), Trường `bao gồm trong đăng ký đóng góp từ lương` là True
            Mẫu phụ cấp (MEAL), Trường `bao gồm trong đăng ký đóng góp từ lương` là False
        """
        AdvantageTemplate = self.env['hr.advantage.template']
        advantage_travel = AdvantageTemplate.search([('company_id', '=', self.env.company.id), ('code', '=', 'TRAVEL')])
        advantage_travel.included_in_payroll_contribution_register = True
        advantage_phone = AdvantageTemplate.search([('company_id', '=', self.env.company.id), ('code', '=', 'PHONE')])
        advantage_meal = AdvantageTemplate.search([('company_id', '=', self.env.company.id), ('code', '=', 'MEAL')])
        self.contract_open_emp_A.write({
            'advantage_ids': [
                                (0, 0, {'template_id': advantage_travel.id, 'amount': 500}),
                                (0, 0, {'template_id': advantage_phone.id, 'amount': 500}),
                                (0, 0, {'template_id': advantage_meal.id, 'amount': 500, 'included_in_payroll_contribution_register': True}),
                            ],
        })

        self.assertRecordValues(
            self.contract_open_emp_A.advantage_ids,
            [{
                'included_in_payroll_contribution_register': True,
            },
            {
                'included_in_payroll_contribution_register': False,
            },
            {
                'included_in_payroll_contribution_register': True,
            }])
        self.assertFalse(advantage_meal.included_in_payroll_contribution_register)

    # 3. Hợp đồng: hr.contract
    def test_advantages_included_contribution_register_1(self):
        """
        Hợp đồng lương 10000, chưa có kiểu và đăng ký đóng góp từ lương
        Phụ cấp TRAVEL cho hợp đồng là 500, không đánh dấu là bao gồm trong đăng ký đóng góp từ lương
        Chọn kiểu đăng ký đóng góp từ lương
        Nhấn chọn tạo đăng ký đóng góp từ lương
        
        => Tạo ra các dòng đăng ký đóng góp từ lương với cơ sở tính toán là 10000
        
        """
        contract = self.contract_open_emp_A
        advantage = self.env['hr.advantage.template'].search([('company_id', '=', self.env.company.id), ('code', '=', 'TRAVEL')])
        contribution_types = self.env['hr.payroll.contribution.type'].search([('company_id', '=', self.env.company.id)], limit=4)
        contract.write({
            'wage': 10000,
            'advantage_ids': [(0, 0, {'template_id': advantage.id, 'amount': 500, 'included_in_payroll_contribution_register': False})],
            'payroll_contribution_type_ids': [(6, 0, contribution_types.ids)]
        })
        contract.generate_payroll_contribution_registers()
        self.assertRecordValues(
            contract.payroll_contribution_register_ids,
            [{
                'contribution_base': 10000,
            },
            {
                'contribution_base': 10000,
            },
            {
                'contribution_base': 10000,
            },
            {
                'contribution_base': 10000,
            }])

    # 3. Hợp đồng: hr.contract
    def test_advantages_included_contribution_register_2(self):
        """
        Hợp đồng lương 10000, chưa có kiểu và đăng ký đóng góp từ lương
        Phụ cấp TRAVEL cho hợp đồng là 500, có đánh dấu là bao gồm trong đăng ký đóng góp từ lương
        Chọn kiểu đăng ký đóng góp từ lương
        Nhấn chọn tạo đăng ký đóng góp từ lương
        
        => Tạo ra các dòng đăng ký đóng góp từ lương với cơ sở tính toán là 10500
        
        """
        contract = self.contract_open_emp_A
        advantage = self.env['hr.advantage.template'].search([('company_id', '=', self.env.company.id), ('code', '=', 'TRAVEL')])
        contribution_types = self.env['hr.payroll.contribution.type'].search([('company_id', '=', self.env.company.id)], limit=4)
        contract.write({
            'wage': 10000,
            'advantage_ids': [(0, 0, {'template_id': advantage.id, 'amount': 500, 'included_in_payroll_contribution_register': True})],
            'payroll_contribution_type_ids': [(6, 0, contribution_types.ids)]
        })
        contract.generate_payroll_contribution_registers()
        self.assertRecordValues(
            contract.payroll_contribution_register_ids,
            [{
                'contribution_base': 10500,
            },
            {
                'contribution_base': 10500,
            },
            {
                'contribution_base': 10500,
            },
            {
                'contribution_base': 10500,
            }])
