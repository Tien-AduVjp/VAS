from odoo.tests.common import SavepointCase
from odoo import fields


class CommonOverTimeApproval(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(CommonOverTimeApproval, cls).setUpClass()
        cls.employee_1 = cls.env.ref('hr.employee_al')
        cls.employee_2 = cls.env.ref('hr.employee_han')
        cls.contract_employee_1 = cls.env.ref('hr_contract.hr_contract_al')
        cls.approve_type_overtime = cls.env['approval.request.type'].search([('type', '=', 'overtime')], limit=1)
        cls.approve_type_generic = cls.env['approval.request.type'].search([('type', '=', 'generic')], limit=1)

        # Overtime Approval: only supports test cases
        cls.overtime_approval_request = cls.env['approval.request'].create({
            'title': 'Overtime Approval Request Test',
            'employee_id': cls.env.ref('base.user_admin').employee_id.id,
            'approval_type_id': cls.approve_type_overtime.id,
            'company_id': cls.env.company.id,
            'currency_id': cls.env.company.currency_id.id,
            'deadline': fields.Date.today()
        })

        # Genric Approval: only supports test cases
        cls.generic_approval_request = cls.env['approval.request'].with_context(tracking_disable=True).create({
            'title': 'Generic Approval Request Test',
            'employee_id': cls.env.ref('base.user_admin').employee_id.id,
            'approval_type_id': cls.approve_type_generic.id,
            'company_id': cls.env.company.id,
            'currency_id': cls.env.company.currency_id.id,
            'deadline': fields.Date.today()
        })

        #Reason Overtime
        cls.reason_general = cls.env.ref('viin_hr_overtime.hr_overtime_reason_general')

        # Overtime Plan
        cls.overtime_plan_1 = cls.env['hr.overtime.plan'].with_context(tracking_disable=True).create({
            'employee_id': cls.employee_1.id,
            'recognition_mode': 'none',
            'reason_id': cls.reason_general.id,
            'time_start': 17,
            'time_end': 18,
            'approval_id': cls.overtime_approval_request.id
        })
        cls.overtime_plan_2 = cls.env['hr.overtime.plan'].with_context(tracking_disable=True).create({
            'employee_id': cls.employee_1.id,
            'recognition_mode': 'none',
            'reason_id': cls.reason_general.id,
            'time_start': 18,
            'time_end': 19,
        })
        cls.overtime_plan_3 = cls.env['hr.overtime.plan'].with_context(tracking_disable=True).create({
            'employee_id': cls.employee_2.id,
            'recognition_mode': 'none',
            'reason_id': cls.reason_general.id,
            'time_start': 17,
            'time_end': 18,
        })
