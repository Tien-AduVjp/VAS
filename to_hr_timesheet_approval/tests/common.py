from datetime import date

from odoo.tests.common import SavepointCase
from odoo import fields


class CommonTimesheetApproval(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(CommonTimesheetApproval, cls).setUpClass()
        group_hr_timesheet_user = cls.env.ref('hr_timesheet.group_hr_timesheet_user')
        group_hr_timesheet_approver = cls.env.ref('hr_timesheet.group_hr_timesheet_approver')
        group_user = cls.env.ref('base.group_user')
        cls.employee_1 = cls.env.ref('hr.employee_al')
        cls.employee_2 = cls.env.ref('hr.employee_jog')
        cls.employee_3 = cls.env.ref('hr.employee_jep')
        cls.user_1 = cls.env['res.users'].with_context(tracking_disable=True, no_reset_password=True).create({
            'name': 'User 1',
            'login': 'user1',
            'email': 'user1@example.viindoo.com',
            'groups_id': [(6, 0, [group_user.id, group_hr_timesheet_approver.id])]
        })
        cls.user_no_employee = cls.env['res.users'].with_context(tracking_disable=True, no_reset_password=True).create({
            'name': 'User 2',
            'login': 'user2',
            'email': 'user2@example.viindoo.com',
            'groups_id': [(6, 0, [group_user.id, group_hr_timesheet_user.id])]
        })

        cls.department_a = cls.env['hr.department'].create({
            'name': 'Department A',
            'timesheet_approval': True
        })
        cls.department_b = cls.env['hr.department'].create({
            'name': 'Department B',
            'parent_id': cls.department_a.id
        })

        cls.job_position_1 = cls.env['hr.job'].create({
            'name': 'Job 1',
        })
        cls.contract_employee_1 = cls.env.ref('hr_contract.hr_contract_al')
        cls.contract_employee_1.write({
            'date_start': date(2021, 10, 10),
            'wage': 10000000.0,
            'date_end': date.max,
            'timesheet_approval': True,
        })

        cls.project = cls.env.ref('project.project_project_2')
        cls.project.write({'allowed_internal_user_ids': [(4, cls.user_1.id, 0)]})
        cls.env['account.analytic.line'].search([('employee_id', '=', cls.employee_1.id)]).unlink()
        cls.timesheet_1 = cls.env['account.analytic.line'].create({
            'name': 'Timesheet Employee 1',
            'project_id': cls.project.id,
            'employee_id': cls.employee_1.id,
            'unit_amount': 1,
        })
        cls.timesheet_2 = cls.env['account.analytic.line'].create({
            'name': 'Timesheet Employee 1',
            'project_id': cls.project.id,
            'employee_id': cls.employee_1.id,
            'unit_amount': 2,
        })
        cls.timesheet_3 = cls.env['account.analytic.line'].create({
            'name': 'Timesheet Employee 2',
            'project_id': cls.project.id,
            'employee_id': cls.employee_2.id,
            'unit_amount': 1,
        })
        cls.timesheet_4 = cls.env['account.analytic.line'].create({
            'name': 'Timesheet Employee 3',
            'project_id': cls.project.id,
            'employee_id': cls.employee_3.id,
            'unit_amount': 1,
        })

        cls.approve_type_timesheet = cls.env['approval.request.type'].search([('type', '=', 'timesheets')], limit=1)
        cls.approve_type_generic = cls.env['approval.request.type'].search([('type', '=', 'generic')], limit=1)

        cls.timesheet_approve_request_employee = cls.env['approval.request'].create({
            'title': 'Timesheet Approval Request Employee 1',
            'employee_id': cls.employee_1.id,
            'approval_type_id': cls.approve_type_timesheet.id,
            'company_id': cls.env.company.id,
            'currency_id': cls.env.company.currency_id.id,
            'deadline': fields.Date.today()
        })
