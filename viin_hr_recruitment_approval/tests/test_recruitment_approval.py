from odoo.tests.common import tagged
from odoo import fields

from .common import Common


@tagged('-at_install', 'post_install')
class TestRequestApproval(Common):

    @classmethod
    def setUpClass(cls):
        super(TestRequestApproval, cls).setUpClass()

        cls.approve_type_both = cls.env['approval.request.type'].create({
            'name':'Manager & HR',
            'type':'recruitment',
            'mimimum_approvals': 2,
            'sequential_approvals': True,
            'manager_approval': 'required',
            'type_approval_user_line_ids':[
                (0, 0, {
                    'user_id': cls.approval_officer_user.id,
                    'required': True
                }),
                (0, 0, {
                    'user_id': cls.approval_officer_user_02.id,
                    'required': False
                }),

            ]
            })

        cls.employee1_user.employee_id.department_id = cls.hr_job.department_id
        cls.recruitment_approval_request = cls.env['approval.request'].with_user(cls.employee1_user).create({
            'title': 'Recruitment Approval Request',
            'approval_type_id': cls.type_multiple_approvers.id,
            'currency_id':cls.env.company.currency_id.id,
            'job_id': cls.hr_job.id,
            'description': 'need for project',
            'description_job': 'description',
            'requirements': 'requirements',
            'deadline': fields.Date.today()
            })
        cls.recruitment_approval_request.with_user(cls.env.ref('base.user_admin')).request_approval_user_line_ids[0].required = False

    def test_data_init_generate(self):
        approval_recruitment_type = self.env['approval.request.type'].search([('type', '=', 'recruitment')], limit=1)
        self.assertRecordValues(
            approval_recruitment_type,
            [
                {
                    'name': 'Recruitment Approval',
                    'type': "recruitment"
                }
            ]
        )
        self.assertEqual(approval_recruitment_type.type_approval_user_line_ids[0].user_id.id, self.env.ref('base.user_admin').id)
        self.assertTrue(approval_recruitment_type.type_approval_user_line_ids[0].required)

    def test_01_request_approval_recruitment(self):
        self.assertRecordValues(
            self.recruitment_approval_request,
             [
                {
                    'approval_type_id': self.type_multiple_approvers.id,
                    'employee_id': self.employee1_user.employee_id.id,
                    'state': 'draft',
                    'job_id': self.hr_job.id,
                    }
                ]
            )
        #Employee: action confirm request
        self.recruitment_approval_request.with_user(self.employee1_user).action_confirm()
        self.assertEqual(self.recruitment_approval_request.state, 'confirm')
        self.recruitment_approval_request.with_user(self.team_leader_user_01).action_validate()
        self.recruitment_approval_request.with_user(self.approval_officer_user_01).action_validate()
        self.recruitment_approval_request.with_user(self.approval_officer_user_02).action_validate()
        self.assertEqual(self.recruitment_approval_request.state, 'validate')
        #Employee: action done request
        self.recruitment_approval_request.with_user(self.team_leader_user_01).action_done()
        self.assertEqual(self.recruitment_approval_request.state, 'done')

    def test_05_request_approval_recruitment(self):
        # Manager & Officer Approve
        # Employee creates approval request with type manager & officer approval
        self.recruitment_approval_request.write({'approval_type_id': self.type_multiple_approvers.id})
        self.assertEqual(self.recruitment_approval_request.approval_type_id.id, self.type_multiple_approvers.id)
        #Employee: action confirm request
        self.recruitment_approval_request.with_user(self.employee1_user).action_confirm()
        self.assertEqual(self.recruitment_approval_request.state, 'confirm')

        #The manager received the notification
        self.assertEqual(self.recruitment_approval_request.activity_ids[-1].user_id.id, self.team_leader_user_01.id)
        #Manager: action approve
        self.recruitment_approval_request.with_user(self.team_leader_user_01).action_validate()
        self.assertEqual(self.recruitment_approval_request.state, 'confirm')

        #The officer received the notification
        self.assertEqual(self.recruitment_approval_request.activity_ids[-1].user_id.id, self.approval_officer_user_01.id)
        #Officer: action validate
        self.recruitment_approval_request.with_user(self.approval_officer_user_01).action_validate()
        self.assertEqual(self.recruitment_approval_request.state, 'confirm')
        #The officer received the notification
        self.assertEqual(self.recruitment_approval_request.activity_ids[-1].user_id.id, self.approval_officer_user_02.id)
        #Officer: action validate
        self.recruitment_approval_request.with_user(self.approval_officer_user_02).action_validate()
        self.assertEqual(self.recruitment_approval_request.state, 'validate')
        #Officer: action done
        self.recruitment_approval_request.with_user(self.team_leader_user_01).action_done()
        self.assertEqual(self.recruitment_approval_request.state, 'done')

    def test_06_request_approval_recruitment(self):
        #Employee: action confirm request
        self.recruitment_approval_request.with_user(self.employee1_user).action_confirm()
        self.assertEqual(self.recruitment_approval_request.state, 'confirm')

        #The manager received the notification
        self.assertEqual(self.recruitment_approval_request.activity_ids[-1].user_id.id, self.team_leader_user_01.id)
        #Manager: action refuse
        self.recruitment_approval_request.with_user(self.team_leader_user_01).action_refuse()
        self.assertEqual(self.recruitment_approval_request.state, 'confirm')
        self.recruitment_approval_request.with_user(self.approval_officer_user_01).action_refuse()
        self.assertEqual(self.recruitment_approval_request.state, 'refuse')


    def test_07_request_approval_recruitment(self):
        #Employee: action confirm request
        self.recruitment_approval_request.with_user(self.employee1_user).action_confirm()
        self.assertEqual(self.recruitment_approval_request.state, 'confirm')

        #The manager received the notification
        self.assertEqual(self.recruitment_approval_request.activity_ids[-1].user_id.id, self.team_leader_user_01.id)

        #Admin approve
        self.recruitment_approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).action_validate()
        self.assertEqual(self.recruitment_approval_request.state, 'validate')

        #Admin: action done
        self.recruitment_approval_request.with_user(self.env.ref('base.user_admin')).action_done()
        self.assertEqual(self.recruitment_approval_request.state, 'done')
