from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.exceptions import UserError
from odoo.tools.misc import mute_logger

from . import common


@tagged('post_install', '-at_install')
class TestApprovalRequest(common.Common):

    def test_01_min_approvals(self):
        with self.assertRaises(UserError):
            self.type_multiple_approvers.mimimum_approvals = 2
        with self.assertRaises(UserError):
            self.env['approval.request.type'].create({
                'name':'Multiple Approvers with sequence',
                'type':'generic',
                'mimimum_approvals': 2,
                'sequential_approvals': True,
                'manager_approval': 'required',
                'type_approval_user_line_ids':[
                    (0, 0, {
                        'user_id': self.approval_officer_user_01.id,
                        'required': True
                    }),
                    (0, 0, {
                        'user_id': self.approval_officer_user_02.id,
                        'required': True
                    }),
                    (0, 0, {
                        'user_id': self.approval_officer_user_03.id,
                        'required': False
                    }),
                    ]
                })

        try:
            self.env['approval.request.type'].create({
                'name':'Multiple Approvers with sequence',
                'type':'generic',
                'mimimum_approvals': 1,
                'sequential_approvals': True,
                'manager_approval': 'optional',
                'type_approval_user_line_ids':[
                    (0, 0, {
                        'user_id': self.approval_officer_user_01.id,
                        'required': True
                    }),
                    (0, 0, {
                        'user_id': self.approval_officer_user_02.id,
                        'required': False
                    }),
                    ]
                })
        except UserError:
            self.fail("Error should not raise here.")

    def test_days_to_approve_is_negative(self):
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.type_multiple_approvers.write({'days_to_approve': -1})
            self.type_multiple_approvers.flush()
