from odoo.tests import SavepointCase
from odoo import fields


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        cls.department2 = cls.env['hr.department'].create({
            'name': "Department 2",
            })
        cls.department1 = cls.env['hr.department'].create({
            'name': "Department 1",
            'parent_id': cls.department2.id
            })
        """
        1. employee1 => employee2 => team_leader1 =>
        2. employee3 => team_leader2
        3.
        """
        # normal employee users
        cls.employee1_user = cls.env.ref('to_approvals.employee1_user_demo')
        cls.employee1_user.action_create_employee()
        cls.employee1 = cls.employee1_user.employee_id

        cls.employee2_user = cls.env.ref('to_approvals.employee2_user_demo')
        cls.employee2_user.action_create_employee()
        cls.employee2 = cls.employee2_user.employee_id

        cls.employee3_user = cls.env.ref('to_approvals.employee3_user_demo')
        cls.employee3_user.action_create_employee()
        cls.employee3 = cls.employee3_user.employee_id

        cls.team_leader_user_01 = cls.env.ref('to_approvals.team_leader_user_01_demo')
        cls.team_leader_user_01.action_create_employee()
        cls.team_leader1 = cls.team_leader_user_01.employee_id

        cls.team_leader_user_02 = cls.env.ref('to_approvals.team_leader_user_02_demo')
        cls.team_leader_user_02.action_create_employee()
        cls.team_leader2 = cls.team_leader_user_02.employee_id

        cls.department_manager_user_01 = cls.env.ref('to_approvals.department_manager_user_01_demo')
        cls.department_manager_user_01.action_create_employee()
        cls.department_manager1 = cls.department_manager_user_01.employee_id

        cls.parent_department_manager_user_01 = cls.env.ref('to_approvals.parent_department_manager_user_01_demo')
        cls.parent_department_manager_user_01.action_create_employee()
        cls.department_manager2 = cls.parent_department_manager_user_01.employee_id

        (cls.employee1 + cls.employee2 + cls.team_leader1).write({
            'department_id': cls.department1.id
            })
        cls.employee1.parent_id = cls.employee2
        cls.employee2.parent_id = cls.team_leader1
        cls.team_leader1.parent_id = cls.department_manager1

        (cls.employee3 + cls.team_leader2 + cls.department_manager2).write({
            'department_id': cls.department2.id
            })
        cls.employee3.parent_id = cls.team_leader2

        # approval officer users
        cls.approval_officer_user = cls.env.ref('to_approvals.approval_officer_user_demo')
        cls.approval_officer_user_01 = cls.env.ref('to_approvals.approval_officer_user_01_demo')
        cls.approval_officer_user_02 = cls.env.ref('to_approvals.approval_officer_user_02_demo')
        cls.approval_officer_user_03 = cls.env.ref('to_approvals.approval_officer_user_03_demo')
        RequestType = cls.env['approval.request.type']
        cls.type_multiple_approvers = RequestType.create({
            'name':'Multiple Approvers with sequence',
            'type':'generic',
            'mimimum_approvals': 3,
            'sequential_approvals': True,
            'manager_approval': 'required',
            'type_approval_user_line_ids':[
                (0, 0, {
                    'user_id': cls.approval_officer_user_01.id,
                    'required': True
                }),
                (0, 0, {
                    'user_id': cls.approval_officer_user_02.id,
                    'required': True
                }),
                (0, 0, {
                    'user_id': cls.approval_officer_user_03.id,
                    'required': False
                }),
            ]
            })

        cls.type_multiple_approver_01 = RequestType.create({
            'name':'Multiple Approvers without sequence',
            'type':'generic',
            'mimimum_approvals': 3,
            'sequential_approvals': False,
            'manager_approval': 'required',
            'type_approval_user_line_ids':[
                (0, 0, {
                    'user_id': cls.approval_officer_user_01.id,
                    'required': True
                }),
                (0, 0, {
                    'user_id': cls.approval_officer_user_02.id,
                    'required': True
                }),
                (0, 0, {
                    'user_id': cls.approval_officer_user_03.id,
                    'required': False
                }),
                ]
            })
        ApprovalRequest = cls.env['approval.request']
        cls.approval_request = ApprovalRequest.with_user(cls.employee1_user).create({
            'title':'Approval request',
            'approval_type_id': cls.type_multiple_approvers.id,
            'currency_id': cls.env.company.currency_id.id,
            'employee_id': cls.employee1_user.employee_id.id,
            'deadline': fields.Date.today()
            })
        cls.approval_request_01 = ApprovalRequest.with_user(cls.employee1_user).create({
            'title':'Approval request 01',
            'approval_type_id': cls.type_multiple_approver_01.id,
            'currency_id': cls.env.company.currency_id.id,
            'employee_id': cls.employee1_user.employee_id.id,
            'deadline': fields.Date.today()
            })
