from odoo import fields
from odoo.tests.common import SavepointCase

ADVANTAGE_CODE_LIST = ['TRAVEL', 'PHONE', 'MEAL', 'RESPONSIBILITY', 'HARDWORK', 'PERFORMANCE', 'HARMFUL']


class TestPayrollCommon(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestPayrollCommon, cls).setUpClass()
                
        # Set country by currency
        currency = cls.env.company.currency_id
        country = cls.env['res.country'].search([('currency_id', '=', currency.id)], limit=1)
        cls.env.company.write({
            'country_id': country.id,
            'payslips_auto_generation': False
        })
        
        cls.env['hr.leave.type'].search([('company_id', '=', cls.env.company.id)]).write({
            'validity_start': fields.Date.to_date('2020-01-01')
        })

        # Job
        cls.job_product_dev = cls.create_job('Product Developer', 7500000)
        cls.job_product_manager = cls.create_job('Product Department - Manager', 10000000)
        
        # Employee
        cls.product_emp_A = cls.create_employee(
            'Product Employee 1',
            job_id=cls.job_product_dev.id)
        cls.product_dep_manager = cls.create_employee(
            'Product Department Manager',
            job_id=cls.job_product_manager.id)
        
        # Department
        members = [cls.product_emp_A.id, cls.product_dep_manager.id]
        cls.product_department = cls.create_department(
            'Product Department',
        cls.product_dep_manager.id,
        members)
        
        # personal tax
        cls.personal_tax_rule = cls.env['personal.tax.rule'].create({
            'country_id': cls.env.company.country_id.id,
            'apply_tax_base_deduction': True,
            'personal_tax_policy': 'escalation',
            'personal_tax_base_ded': 11000000,
            'dependent_tax_base_ded': 4400000,
            'progress_ids': [
                    (0, 0, {'base': 0, 'rate': 5.0}),
                    (0, 0, {'base': 5000000, 'rate': 10.0}),
                    (0, 0, {'base': 10000000, 'rate': 15.0}),
                    (0, 0, {'base': 18000000, 'rate': 20.0}),
                    (0, 0, {'base': 32000000, 'rate': 25.0}),
                    (0, 0, {'base': 52000000, 'rate': 30.0}),
                    (0, 0, {'base': 80000000, 'rate': 35.0})
                ]
        })
                
        # base salary structure
        cls.structure_base = cls.env['hr.payroll.structure'].search(
            [('company_id', '=', cls.env.company.id),
             ('code', '=', 'BASE')], limit=1)
        
        # Contract: 4 states
        cls.contract_open_emp_A = cls.create_contract(
            cls.product_emp_A.id,
            fields.Date.from_string('2021-1-1'),
            fields.Date.from_string('2021-12-31'),
            'open')
        cls.contract_draft_emp_A = cls.create_contract(
            cls.product_emp_A.id,
            fields.Date.from_string('2021-1-1'),
            fields.Date.from_string('2021-12-31'),
            'draft')
        cls.contract_cancel_emp_A = cls.create_contract(
            cls.product_emp_A.id,
            fields.Date.from_string('2021-1-1'),
            fields.Date.from_string('2021-12-31'),
            'cancel')
        cls.contract_close_emp_A = cls.create_contract(
            cls.product_emp_A.id,
            fields.Date.from_string('2020-1-1'),
            fields.Date.from_string('2020-12-31'),
            'close')

        # Set amount (min,max) for advantage template
        vals = {'amount':0, 'lower_bound': 0, 'upper_bound': 1000000}
        cls.env['hr.advantage.template'].search([('company_id', '=', cls.env.company.id)]).write(vals)
        
        # Set Leave Type 
        paid_type = cls.env['hr.leave.type'].search(
            [('company_id', '=', cls.env.company.id),
             ('unpaid', '=', False),
             ('code', '=', 'PaidTimeOff')],
            limit=1)
        paid_type.write({
            'allocation_type': 'no',
            'validity_start': fields.Date.from_string('2021-1-1')
        })
        
        # Others
        # Category : ALW
        RuleCategory = cls.env['hr.salary.rule.category']
        alw_category = RuleCategory.search(
            [('code', '=', 'ALW'),
             ('company_id', '=', cls.env.company.id)])
        cls.alw_categories = RuleCategory.search(
            [('company_id', '=', cls.env.company.id),
             ('parent_id', 'child_of', alw_category.id)])
        
        # Category : ALWNOTAX
        alwnotax_category = RuleCategory.search(
            [('code', '=', 'ALWNOTAX'),
             ('company_id', '=', cls.env.company.id)])
        cls.alwnotax_categories = RuleCategory.search(
            [('company_id', '=', cls.env.company.id),
             ('parent_id', 'child_of', alwnotax_category.id)])
        
        # DED_BEFORE_TAX
        ded_before_tax_category = RuleCategory.search(
            [('code', '=', 'DED_BEFORE_TAX'),
             ('company_id', '=', cls.env.company.id)])
        cls.ded_before_tax_categories = RuleCategory.search(
            [('parent_id', 'child_of', ded_before_tax_category.id),
             ('company_id', '=', cls.env.company.id)])
        
        # DED_AFTER_TAX
        ded_after_tax_category = RuleCategory.search(
            [('code', '=', 'DED_AFTER_TAX'),
             ('company_id', '=', cls.env.company.id)])
        cls.ded_after_tax_categories = RuleCategory.search(
            [('parent_id', 'child_of', ded_after_tax_category.id),
             ('company_id', '=', cls.env.company.id)])
        
        # PTAX
        ptax_category = RuleCategory.search([
            ('code', '=', 'PTAX'),
            ('company_id', '=', cls.env.company.id)])
        cls.ptax_categories = RuleCategory.search(
            [('parent_id', 'child_of', ptax_category.id),
             ('company_id', '=', cls.env.company.id)])
        
    @classmethod
    def create_user(cls, name, login, email_name, groups_ids):
        Users = cls.env['res.users'].with_context({
            'no_reset_password': True,
            'mail_create_nosubscribe': True
        })
        return Users.create({
            'name': name, 'login': login,
            'email': '%s@example.viindoo.com' % (email_name),
            'groups_id': [(6, 0, groups_ids)]
        })
    
    @classmethod
    def create_employee(cls, name, job_id=None, department_id=None):
        asdress_home_id = cls.create_partner('name')
        return  cls.env['hr.employee'].with_context(tracking_disable=True).create({
            'name': name,
            'job_id': job_id,
            'department_id': department_id,
            'address_home_id': asdress_home_id.id
        })
    
    @classmethod
    def create_partner(cls, name):
        return cls.env['res.partner'].with_context(tracking_disable=True).create({
            'name': name,
            'country_id': cls.env.company.country_id.id
        })
    
    @classmethod
    def create_contract(cls, employee_id, start, end=None, state='open', wage=None, department_id=False, job_id=False):
        return cls.env['hr.contract'].with_context(tracking_disable=True).create({
            'name': 'Contract',
            'employee_id': employee_id,
            'state': state,
            'date_start': start,
            'date_end': end,
            'kanban_state': 'normal',
            'wage': wage or 15000000,
            'personal_tax_rule_id': cls.personal_tax_rule.id,
            'struct_id': cls.structure_base.id,
            'department_id': department_id or cls.product_department.id,
            'job_id': job_id or cls.job_product_dev.id
        })
    
    @classmethod
    def create_department(cls, name, manager_id=False, employee_ids=[]):
        return cls.env['hr.department'].with_context(tracking_disable=True).create({
                'name': name,
                'manager_id': manager_id,
                'member_ids': [(6, 0, employee_ids)]
            })
    
    @classmethod
    def create_job(cls, name, wage):
        return cls.env['hr.job'].with_context(tracking_disable=True).create({'name': name, 'wage': wage})
    
    @classmethod
    def create_rule(cls, name, code, struct_id, category_id, register_id=False):
        return cls.env['hr.salary.rule'].with_context(tracking_disable=True).create({
            'name': name,
            'code': code,
            'struct_id': struct_id,
            'category_id': category_id,
            'register_id': register_id
        })
    
    @classmethod
    def prepare_rule_data(cls, name, code, struct_id, category_id, register_id=False):
        return {
            'name': 'name',
            'code': 'code',
            'struct_id': struct_id,
            'category_id': category_id,
            'register_id': register_id
        }
    
    @classmethod
    def create_payslip(cls, employee_id, start, end, contract_id, thirteen_month_pay=False, trial=False):
        return cls.env['hr.payslip'].with_context(tracking_disable=True).create({
            'employee_id': employee_id,
            'date_from': start,
            'date_to': end,
            'thirteen_month_pay': thirteen_month_pay,
            'thirteen_month_pay_include_trial': trial,
            'contract_id': contract_id,
            'company_id': cls.env.company.id,
        })
    
    @classmethod
    def create_payslip_input_line(cls, payslip, name, code, amount=0, rule_id=None):
        return cls.env['hr.payslip.input'].with_context(tracking_disable=True).create({
            'payslip_id': payslip.id,
            'name': name,
            'code': code,
            'amount': amount,
            'salary_rule_id': rule_id,
            'contract_id': payslip.contract_id.id,
        })
    
    @classmethod
    def create_holiday(cls, name, employee_id, holiday_status_id, date_from, date_to):
        return cls.env['hr.leave'].with_context(tracking_disable=True).create({
            'name': name,
            'employee_id': employee_id,
            'holiday_status_id': holiday_status_id,
            'date_from': date_from,
            'date_to': date_to,
        })
    
    @classmethod
    def create_contrib_register(cls, employee, type, date_from=False, state=False, employee_rate=0, company_rate=0, contrib_base=0):
        ContribRegister = cls.env['hr.payroll.contribution.register']
        return ContribRegister.with_context(tracking_disable=True).create({
            'employee_id': employee.id,
            'type_id': type.id,
            'date_from': date_from or fields.Date.from_string('2021-1-1'),
            'state': state or 'draft',
            'employee_contrib_rate': employee_rate,
            'company_contrib_rate': company_rate,
            'contribution_base': contrib_base
            })
