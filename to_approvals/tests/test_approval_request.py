from odoo.tests import tagged
from odoo.exceptions import UserError
from odoo import fields

from . import common


@tagged('post_install', '-at_install')
class TestApprovalRequest(common.Common):

    def test_01_01_compute_approvers(self):
        """
            [Test case] Kiểm tra số phiếu duyệt tối thiểu.
            Input: Khi số phiểu duyệt tối thiểu lớn hơn số người trong danh sách duyệt.
            Expect: Hiển thị cảnh báo.
        """
        self.assertFalse(self.type_multiple_approvers.mimimum_approvals_exceed_warning)
        self.type_multiple_approvers.mimimum_approvals = 5
        self.assertTrue(self.type_multiple_approvers.mimimum_approvals_exceed_warning)

    def test_01_02_compute_approvers(self):
        """
            [Test case] Kiểm tra tính toán danh sách người phê duyệt.
            Input: Khi trường quản lý phê duyệt được đánh dấu yêu cầu.
            Expect: Danh sách người duyệt sẽ tự động thêm quản lý của nhân viên.
        """
        # Quản lý của nhân viên tự động được thêm vào danh sách duyệt
        self.assertEqual(self.approval_request.approver_ids,
                         self.team_leader_user_01 |
                         self.approval_officer_user_01 |
                         self.approval_officer_user_02 |
                         self.approval_officer_user_03
                        )

    def test_01_03_compute_approvers(self):
        """"
            [Test case] Kiểm tra tính toán line duyệt.
            Input: Khi trường quản lý phê duyệt không được đánh dấu yêu cầu.
            Expect: Danh sách người duyệt sẽ không bao gồm quản lý của nhân viên.
        """
        type_multiple_approvers = self.env['approval.request.type'].create({
            'name':'Multiple Approvers with sequence',
            'type':'generic',
            'mimimum_approvals': 3,
            'sequential_approvals': True,
            'manager_approval': 'none',
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
        approval_request = self.env['approval.request'].with_user(self.employee1_user).create({
            'title':'Approval request',
            'approval_type_id': type_multiple_approvers.id,
            'currency_id': self.env.company.currency_id.id,
            'employee_id': self.employee1_user.employee_id.id,
            'deadline': fields.Date.today()
            })

        self.assertEqual(
            approval_request.approver_ids,
            self.approval_officer_user_01 | self.approval_officer_user_02 | self.approval_officer_user_03
            )
        type_multiple_approvers.manager_approval = 'optional'
        approval_request = self.env['approval.request'].with_user(self.employee1_user).create({
            'title':'Approval request',
            'approval_type_id': type_multiple_approvers.id,
            'currency_id': self.env.company.currency_id.id,
            'employee_id': self.employee1_user.employee_id.id,
            'deadline': fields.Date.today()
            })
        self.assertEqual(
            approval_request.approver_ids,
            self.team_leader_user_01 | self.approval_officer_user_01 | self.approval_officer_user_02 | self.approval_officer_user_03
            )

    def test_04_01_compute_state(self):
        """
            [Test case] Kiểm tra tính toán trạng thái của đề nghị trình duyệt.
            Input: Đề nghị trình duyệt sau khi được tạo mới.
            Expect: Đề nghị trình duyệt ở trạng thái dự thảo, trạng thái duyệt của những người trong danh sách duyệt ở trạng thái dự thảo.
        """
        self.assertEqual(self.approval_request.state, 'draft')
        self.assertEqual(
            self.approval_request.request_approval_user_line_ids.mapped('state'),
            ['draft', 'draft', 'draft', 'draft']
            )

    def test_04_02_compute_state(self):
        """
            [Test case] Kiểm tra tính toán trạng thái của đề nghị trình duyệt.
            Input: Đề nghị trình duyệt được xác nhận.
            Expect: Đề nghị trình duyệt ở trạng thái xác nhận, trạng thái duyệt của những người trong danh sách duyệt ở trạng thái chờ duyệt.
        """
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.assertEqual(self.approval_request.state, 'confirm')
        self.assertEqual(
            self.approval_request.request_approval_user_line_ids.mapped('state'),
            ['pending', 'pending', 'pending', 'pending']
            )

    def test_04_03_compute_state(self):
        """
            [Test case] Kiểm tra tính toán trạng thái của đề nghị trình duyệt.
            Input: Đề nghị trình duyệt được xác nhận, có số lượt duyệt chấp nhận nhỏ hơn số duyệt chấp nhận tối thiểu.
            Expect: Đề nghị trình duyệt ở trạng thái xác nhận, người duyệt đã chuyệt có trạng thái đã duyệt, người chưa duyệt sẽ có trạng thái chờ duyệt.
                    Người chưa đến lượt duyệt sẽ không thể chấp nhận hay từ chối trình duyệt.
        """
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.assertEqual(self.approval_request.next_approver_id, self.team_leader_user_01)
        self.approval_request.with_user(self.team_leader_user_01).action_validate()
        self.assertEqual(self.approval_request.state, 'confirm')
        self.assertEqual(
            self.approval_request.request_approval_user_line_ids.mapped('state'),
            ['approved', 'pending', 'pending', 'pending']
            )

        with self.assertRaises(UserError):
            self.approval_request.with_user(self.approval_officer_user_02).action_validate()
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.approval_officer_user_02).action_refuse()
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.approval_officer_user_03).action_validate()
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.approval_officer_user_03).action_refuse()

    def test_04_04_compute_state(self):
        """
            [Test case] Kiểm tra tính toán trạng thái của đề nghị trình duyệt.
            Input: Đề nghị trình duyệt được xác nhận, có số lượt duyệt chấp nhận nhỏ hơn số duyệt chấp nhận tối thiểu.
            Expect: Đề nghị trình duyệt ở trạng thái xác nhận, người duyệt đã chuyệt có trạng thái đã duyệt, người chưa duyệt sẽ có trạng thái chờ duyệt.
                    Người chưa đến lượt duyệt sẽ không thể chấp nhận hay từ chối đề nghị.
        """
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.approval_request.with_user(self.team_leader_user_01).action_validate()
        self.approval_request.with_user(self.approval_officer_user_01).action_validate()
        self.assertEqual(self.approval_request.state, 'confirm')
        self.assertEqual(
            self.approval_request.request_approval_user_line_ids.mapped('state'),
            ['approved', 'approved', 'pending', 'pending']
            )
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.approval_officer_user_03).action_validate()
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.approval_officer_user_03).action_refuse()

    def test_04_05_compute_state(self):
        """
            [Test case] Kiểm tra tính toán trạng thái của đề nghị trình duyệt.
            Input: Đề nghị trình duyệt được xác nhận, có số lượt duyệt chấp nhận bằng số duyệt chấp nhận tối thiểu trong đó bao gồm những người được yêu cầu.
            Expect: Đề nghị trình duyệt ở trạng thái xác nhận, người duyệt đã chuyệt có trạng thái đã duyệt, người chưa duyệt sẽ có trạng thái chờ duyệt.
        """
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.approval_request.with_user(self.team_leader_user_01).action_validate()
        self.approval_request.with_user(self.approval_officer_user_01).action_validate()
        self.approval_request.with_user(self.approval_officer_user_02).action_validate()
        self.assertEqual(self.approval_request.state, 'validate')
        self.assertEqual(
            self.approval_request.request_approval_user_line_ids.mapped('state'),
            ['approved', 'approved', 'approved', 'pending']
            )

    def test_04_06_compute_state(self):
        """
            [Test case] Kiểm tra tính toán trạng thái của đề nghị trình duyệt.
            Input: Số phê duyệt bằng hoặc lớn hơn số người phê duyệt tối thiểu nhưng không đủ người duyệt được yêu cầu.
            Expect: Trình duyệt chưa chuyển sang trạng thái được phê duyệt.
        """
        self.user_approval_officer_04 = self.env['res.users'].create({
            'name':'Approval Officer 04',
            'login':'approval_officer_04',
            'email':'approval_officer_04@example.viindoo.com',
            'groups_id':[6, 0, self.env.ref('to_approvals.group_approval_officer').id]
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).request_approval_user_line_ids = [(0, 0, {
            'user_id': self.user_approval_officer_04.id,
            'required': True
        })]
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.approval_request.with_user(self.team_leader_user_01).action_validate()
        self.approval_request.with_user(self.approval_officer_user_01).action_validate()
        self.approval_request.with_user(self.approval_officer_user_02).action_validate()
        self.approval_request.with_user(self.approval_officer_user_03).action_validate()
        self.assertEqual(self.approval_request.state, 'confirm')
        self.assertEqual(
            self.approval_request.request_approval_user_line_ids.mapped('state'),
            ['approved', 'approved', 'approved', 'approved', 'pending']
            )

    def test_04_07_compute_state(self):
        """
            [Test case] Kiểm tra tính toán trạng thái của đề nghị trình duyệt.
            Input: Số phê duyệt nhỏ hơn số người phê duyệt tối thiểu, có người duyệt là quản lý phê duyệt.
            Expect: Trình duyệt chuyển sang trạng thái được phê duyệt không cần quan tâm kết quả duyệt của người trong line duyệt.
                    Danh sách người duyệt tự động thêm người quản lý phê duyệt có trạng thái đã phê duyệt.
        """
        self.approval_request.with_user(self.employee1_user).action_confirm()
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).action_validate()
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).action_validate()
        self.assertEqual(self.approval_request.state, 'validate')
        self.assertEqual(
            self.approval_request.request_approval_user_line_ids.mapped('state'),
            ['pending', 'pending', 'pending', 'pending']
            )

    def test_04_08_compute_state(self):
        """
            [Test case] Kiểm tra tính toán trạng thái của đề nghị trình duyệt.
            Input: Có 1 người trong danh sách người duyệt từ chối đề nghị.
            Expect: Đề nghị trình duyệt ở trạng thái bị từ chối.
        """
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.approval_request.with_user(self.team_leader_user_01).action_validate()
        self.approval_request.with_user(self.approval_officer_user_01).action_refuse()
        self.assertEqual(self.approval_request.state, 'refuse')
        self.assertEqual(
            self.approval_request.request_approval_user_line_ids.mapped('state'),
            ['approved', 'refused', 'pending', 'pending']
            )

    def test_04_09_compute_state(self):
        """
            [Test case] Kiểm tra tính toán trạng thái của đề nghị trình duyệt.
            Input: Trình duyệt ở trạng thái từ chối nếu số từ chối lớn hơn số người yêu cầu trừ đi số tối thiểu.
            Expect: Đề nghị trình duyệt ở trạng thái bị từ chối.
        """
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.approval_request.with_user(self.team_leader_user_01).action_refuse()
        self.approval_request.with_user(self.approval_officer_user_01).action_validate()
        self.approval_request.with_user(self.approval_officer_user_02).action_validate()
        self.assertEqual(self.approval_request.state, 'refuse')
        self.assertEqual(
            self.approval_request.request_approval_user_line_ids.mapped('state'),
            ['refused', 'approved', 'approved', 'pending']
            )
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.approval_officer_user_03).action_refuse()

    def test_04_10_compute_state(self):
        """
            [Test case] Kiểm tra tính toán trạng thái của đề nghị trình duyệt.
            Input: Quản lý trình duyệt từ chôi đề nghị phê duyệt.
            Expect: Đề nghị phê duyệt chuyển sang trạng thái bị từ chối (không cần quan tâm đến kết quả duyệt của những người trong line duyệt).
        """
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.approval_request.with_user(self.team_leader_user_01).action_refuse()
        self.assertEqual(self.approval_request.state, 'refuse')
        self.assertEqual(
            self.approval_request.request_approval_user_line_ids.mapped('state'),
            ['refused', 'pending', 'pending', 'pending']
            )

    def test_04_11_compute_state(self):
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.approval_request.with_user(self.env.ref('base.user_admin')).action_cancel()
        self.assertEqual(self.approval_request.state, 'cancel')
        self.assertEqual(
            self.approval_request.request_approval_user_line_ids.mapped('state'),
            ['pending', 'pending', 'pending', 'pending']
            )

    def test_04_12_compute_state(self):
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).action_validate()
        self.assertEqual(self.approval_request.state, 'validate')
        self.approval_request.with_user(self.env.ref('base.user_admin')).action_done()
        self.assertEqual(self.approval_request.state, 'done')

    def test_04_13_compute_state(self):
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).action_validate()
        self.assertEqual(self.approval_request.state, 'validate')
        self.approval_request.with_user(self.env.ref('base.user_admin')).action_cancel()
        self.assertEqual(self.approval_request.state, 'cancel')
        self.approval_request.with_user(self.env.ref('base.user_admin')).action_draft()
        self.assertEqual(self.approval_request.state, 'draft')
        self.assertEqual(
            self.approval_request.request_approval_user_line_ids.mapped('state'),
            ['draft', 'draft', 'draft', 'draft']
            )

    def test_04_14_compute_state(self):
        type_multiple_approvers = self.env['approval.request.type'].create({
            'name':'Multiple Approvers without sequence',
            'type':'generic',
            'mimimum_approvals': 3,
            'sequential_approvals': False,
            'manager_approval': 'required',
            'type_approval_user_line_ids':[
                (0, 0, {
                    'user_id': self.approval_officer_user_02.id,
                    'required': False
                }),
                (0, 0, {
                    'user_id': self.approval_officer_user_03.id,
                    'required': False
                }),
                ]
            })
        approval_request = self.env['approval.request'].with_user(self.employee1_user).create({
            'title':'Approval request',
            'approval_type_id': type_multiple_approvers.id,
            'currency_id': self.env.company.currency_id.id,
            'employee_id': self.employee1_user.employee_id.id,
            'deadline': fields.Date.today()
            })
        approval_request.with_user(self.employee1_user).action_confirm()
        self.assertEqual(len(approval_request.request_approval_user_line_ids), 3)
        self.assertEqual(approval_request.state, 'confirm')
        approval_request.with_user(approval_request.request_approval_user_line_ids[0].user_id).action_refuse()
        self.assertEqual(approval_request.state, 'refuse')
        last_progress = 0.0
        for user in approval_request.request_approval_user_line_ids.user_id:
            approval_request.with_user(user).action_validate()
            self.assertAlmostEqual(
                approval_request.progress,
                last_progress + 100.0 / len(approval_request.request_approval_user_line_ids.user_id),
                2)
            last_progress += 100.0 / len(approval_request.request_approval_user_line_ids.user_id)
        self.assertEqual(approval_request.state, 'validate')

    def test_04_19_compute_state(self):
        admin_user = self.env.ref('base.user_admin')
        with self.assertRaises(UserError):
            self.approval_request.with_user(admin_user).action_validate()
        with self.assertRaises(UserError):
            self.approval_request.with_user(admin_user).action_refuse()
        with self.assertRaises(UserError):
            self.approval_request.with_user(admin_user).action_done()
        with self.assertRaises(UserError):
            self.approval_request.with_user(admin_user).action_cancel()

        self.approval_request.with_user(self.employee1_user).action_confirm()
        with self.assertRaises(UserError):
            self.approval_request.with_user(admin_user).action_done()
        with self.assertRaises(UserError):
            self.approval_request.with_user(admin_user).action_draft()

        self.approval_request.with_user(admin_user).with_context(force_approval=True).action_validate()
        with self.assertRaises(UserError):
            self.approval_request.with_user(admin_user).action_refuse()
        with self.assertRaises(UserError):
            self.approval_request.with_user(admin_user).action_draft()
        self.approval_request.with_user(admin_user).with_context(force_approval=True).action_refuse()
        self.approval_request.with_user(admin_user).action_cancel()
        self.assertTrue(self.approval_request.state, 'cancel')
        self.approval_request.with_user(admin_user).action_draft()
        self.assertTrue(self.approval_request.state, 'draft')

    def test_04_20_compute_state(self):
        """
            Kiểm tra tính toán trạng thái của trình duyệt và người phê duyệt khi kiểu trình duyệt không có thứ tự.
        """
        self.approval_request_01.with_user(self.employee1_user).action_confirm()
        self.assertEqual(self.approval_request_01.state, 'confirm')
        self.approval_request_01.with_user(self.approval_officer_user_01).action_validate()
        self.assertEqual(self.approval_request_01.state, 'confirm')
        self.approval_request_01.with_user(self.approval_officer_user_03).action_validate()
        self.assertEqual(self.approval_request_01.state, 'confirm')
        self.approval_request_01.with_user(self.approval_officer_user_02).action_validate()
        self.assertEqual(self.approval_request_01.state, 'confirm')
        self.approval_request_01.with_user(self.team_leader_user_01).action_validate()
        self.assertEqual(self.approval_request_01.state, 'validate')
        # subordinate employee will auto approve by parent
        self.assertEqual(self.approval_request_01.request_approval_user_line_ids[0].state, 'approved')

    def test_04_15_compute_state(self):
        """
        Case: Kiểm tra phê duyệt với tối thiểu 3 người duyệt và 3 người không requied
        Input:
            + Phê duyệt tối thiểu 3 người và 3 người trong line duyệt không requied
            + 1 người từ chối
        Output: Trạng thái là từ chối
        """
        type_multiple_approvers = self.env['approval.request.type'].create({
            'name':'Multiple Approvers without sequence',
            'type':'generic',
            'mimimum_approvals': 3,
            'sequential_approvals': False,
            'manager_approval': 'optional',
            'type_approval_user_line_ids':[
                (0, 0, {
                    'user_id': self.approval_officer_user_02.id,
                    'required': False
                }),
                (0, 0, {
                    'user_id': self.approval_officer_user_03.id,
                    'required': False
                }),
                ]
            })
        approval_request = self.env['approval.request'].with_user(self.employee1_user).create({
            'title':'Approval request',
            'approval_type_id': type_multiple_approvers.id,
            'currency_id': self.env.company.currency_id.id,
            'employee_id': self.employee1_user.employee_id.id,
            'deadline': fields.Date.today()
            })
        approval_request.with_user(self.employee1_user).action_confirm()
        self.assertEqual(len(approval_request.request_approval_user_line_ids), 3)
        self.assertEqual(approval_request.state, 'confirm')
        approval_request.with_user(approval_request.request_approval_user_line_ids[0].user_id).action_refuse()
        self.assertEqual(approval_request.state, 'refuse')
        last_progress = 0.0
        for user in approval_request.request_approval_user_line_ids.user_id:
            approval_request.with_user(user).action_validate()
            self.assertAlmostEqual(
                approval_request.progress,
                last_progress + 100.0 / len(approval_request.request_approval_user_line_ids.user_id),
                2)
            last_progress += 100.0 / len(approval_request.request_approval_user_line_ids.user_id)
        self.assertEqual(approval_request.state, 'validate')

    def test_04_16_compute_state(self):
        """
        Case: Kiểm tra trạng thái của yêu cầu phê duyệt khi thay đổi kiểu
        Input:
            + Kiểu phê duyệt 1, tối thiểu 1 người, không yêu cầu quản lý, có 1 officer or admin trong line duyệt
            + Kiểu phê duyệt 2, tối thiểu 1 người, không yêu cầu quản lý, có 2 officer or admin trong line duyệt
            + Tạo yêu cầu phê duyệt với kiểu 1 trạng thái draft
            + Sửa yêu cầu sang kiểu 2
        Output: Trạng thái của yêu cầu phê duyệt là Draft
        """
        type_multiple_approvers_1 = self.env['approval.request.type'].create({
            'name':'Multiple Approvers without sequence 1',
            'type':'generic',
            'mimimum_approvals': 1,
            'sequential_approvals': False,
            'manager_approval': 'none',
            'type_approval_user_line_ids':[
                (0, 0, {
                    'user_id': self.approval_officer_user_02.id,
                    'required': False
                })
                ]
            })

        type_multiple_approvers_2 = self.env['approval.request.type'].create({
            'name':'Multiple Approvers without sequence 1',
            'type':'generic',
            'mimimum_approvals': 1,
            'sequential_approvals': False,
            'manager_approval': 'none',
            'type_approval_user_line_ids':[
                (0, 0, {
                    'user_id': self.approval_officer_user_02.id,
                    'required': False
                }),
                (0, 0, {
                    'user_id': self.approval_officer_user_03.id,
                    'required': False
                }),
                ]
            })
        approval_request = self.env['approval.request'].with_user(self.employee1_user).create({
            'title':'Approval request',
            'approval_type_id': type_multiple_approvers_1.id,
            'currency_id': self.env.company.currency_id.id,
            'employee_id': self.employee1_user.employee_id.id,
            'deadline': fields.Date.today()
            })
        self.assertEqual(approval_request.state, 'draft')
        approval_request.write({'approval_type_id': type_multiple_approvers_2.id})
        self.assertEqual(approval_request.state, 'draft')

    def test_05_00_direct_manager_in_line_users(self):
        self.team_leader_user_01.groups_id = [(4, self.env.ref('to_approvals.group_approval_officer').id)]

        type_multiple_approvers = self.env['approval.request.type'].create({
            'name':'Multiple Approvers without sequence',
            'type':'generic',
            'mimimum_approvals': 3,
            'sequential_approvals': False,
            'manager_approval': 'required',
            'type_approval_user_line_ids':[
                (0, 0, {
                    'user_id': self.team_leader_user_01.id,
                    'required': True
                }),
                (0, 0, {
                    'user_id': self.approval_officer_user_02.id,
                    'required': True
                }),
                ]
            })
        approval_request = self.env['approval.request'].with_user(self.employee1_user).create({
            'title':'Approval request',
            'approval_type_id': type_multiple_approvers.id,
            'currency_id': self.env.company.currency_id.id,
            'employee_id': self.employee1_user.employee_id.id,
            'deadline': fields.Date.today()
            })
        self.assertEqual(approval_request.mimimum_approvals, 2)
        self.assertEqual(len(approval_request.request_approval_user_line_ids), 2)

        approval_request.with_user(self.employee1_user).action_confirm()
        approval_request.with_user(self.team_leader_user_01).action_validate()
        approval_request.with_user(self.approval_officer_user_02).action_validate()

        self.assertEqual(approval_request.state, 'validate')

    def test_05_01_direct_manager_in_line_users_not_require(self):
        self.team_leader_user_01.groups_id = [(4, self.env.ref('to_approvals.group_approval_officer').id)]

        type_multiple_approvers = self.env['approval.request.type'].create({
            'name':'Multiple Approvers without sequence',
            'type':'generic',
            'mimimum_approvals': 3,
            'sequential_approvals': False,
            'manager_approval': 'required',
            'type_approval_user_line_ids':[
                (0, 0, {
                    'user_id': self.team_leader_user_01.id,
                    'required': False
                }),
                (0, 0, {
                    'user_id': self.approval_officer_user_02.id,
                    'required': True
                }),
                (0, 0, {
                    'user_id': self.approval_officer_user_03.id,
                    'required': True
                }),                ]
            })
        approval_request = self.env['approval.request'].with_user(self.employee1_user).create({
            'title':'Approval request',
            'approval_type_id': type_multiple_approvers.id,
            'currency_id': self.env.company.currency_id.id,
            'employee_id': self.employee1_user.employee_id.id,
            'deadline': fields.Date.today()
            })
        self.assertEqual(approval_request.mimimum_approvals, 3)
        self.assertEqual(len(approval_request.request_approval_user_line_ids), 3)

        approval_request.with_user(self.employee1_user).action_confirm()
        approval_request.with_user(self.team_leader_user_01).action_validate()
        approval_request.with_user(self.approval_officer_user_02).action_validate()
        approval_request.with_user(self.approval_officer_user_03).action_validate()
        self.assertEqual(approval_request.state, 'validate')

    def test_06_01_activity_schedule(self):
        """
        Case: Kiểm tra ấn định hành động phê duyệt cho những người trong danh sách duyệt với kiểu không theo thứ tự
        Input: - Kiểu phê duyệt chung, phê duyệt tối thiểu 2, yêu cầu quản lý phê duyệt, 1 nhân sự phê duyệt
               - Tạo yêu cầu phê duyệt cho nhân viên 1
               - Nhân viên 1 xác nhận phê duyệt
               - Team leader phê duyệt
               - Officer phê duyệt
        Output:
               - Ấn định hành động phê duyệt cho Team Leader và Officer
               - Sau khi Team leader phê duyệt xong không ấn định lặp lại hành động phê duyệt cho Officer
               - Sau khi Team leader và Officer phê duyệt xong thì ấn định hành động hoàn thành
        """
        type_multiple_approvers = self.env['approval.request.type'].create({
            'name':'Multiple Approvers without sequence',
            'type':'generic',
            'mimimum_approvals': 2,
            'sequential_approvals': False,
            'manager_approval': 'required',
            'type_approval_user_line_ids':[
                (0, 0, {
                    'user_id': self.approval_officer_user_01.id,
                    'required': True
                }),
                ]
            })

        approval_request = self.env['approval.request'].with_user(self.employee1_user).create({
            'title':'Approval request',
            'approval_type_id': type_multiple_approvers.id,
            'currency_id': self.env.company.currency_id.id,
            'employee_id': self.employee1_user.employee_id.id,
            'deadline': fields.Date.today()
            })
        approval_request.with_user(self.employee1_user).action_confirm()
        self.assertTrue(approval_request.activity_search(['to_approvals.mail_act_approval'], self.team_leader_user_01.id))
        self.assertTrue(approval_request.activity_search(['to_approvals.mail_act_approval'], self.approval_officer_user_01.id))

        approval_request.with_user(self.team_leader_user_01).action_validate()
        self.assertFalse(approval_request.activity_search(['to_approvals.mail_act_approval'], self.team_leader_user_01.id))
        self.assertTrue(approval_request.activity_search(['to_approvals.mail_act_approval'], self.approval_officer_user_01.id))
        self.assertEqual(len(approval_request.activity_search(['to_approvals.mail_act_approval'], self.approval_officer_user_01.id)), 1)

        approval_request.with_user(self.approval_officer_user_01).action_validate()
        self.assertFalse(approval_request.activity_search(['to_approvals.mail_act_approval'], self.team_leader_user_01.id))
        self.assertFalse(approval_request.activity_search(['to_approvals.mail_act_approval'], self.approval_officer_user_01.id))

    def test_06_02_activity_schedule(self):
        """
        Case: Kiểm tra ấn định hành động phê duyệt cho những người trong danh sách duyệt với kiểu theo thứ tự
        Input: - Kiểu phê duyệt chung, phê duyệt tối thiểu 2, yêu cầu quản lý phê duyệt, 1 nhân sự phê duyệt
               - Tạo yêu cầu phê duyệt cho nhân viên 1
               - Nhân viên 1 xác nhận phê duyệt
               - Team leader phê duyệt
               - Officer phê duyệt
        Output:
               - Ấn định hành động phê duyệt cho Team Leader
               - Sau khi Team leader phê duyệt xong. Ấn định hành động phê duyệt cho Officer
               - Sau khi Team leader và Officer phê duyệt xong thì ấn định hành động hoàn thành
        """
        type_multiple_approvers = self.env['approval.request.type'].create({
            'name':'Multiple Approvers without sequence',
            'type':'generic',
            'mimimum_approvals': 2,
            'sequential_approvals': True,
            'manager_approval': 'required',
            'type_approval_user_line_ids':[
                (0, 0, {
                    'user_id': self.approval_officer_user_01.id,
                    'required': True
                }),
                ]
            })

        approval_request = self.env['approval.request'].with_user(self.employee1_user).create({
            'title':'Approval request',
            'approval_type_id': type_multiple_approvers.id,
            'currency_id': self.env.company.currency_id.id,
            'employee_id': self.employee1_user.employee_id.id,
            'deadline': fields.Date.today()
            })
        approval_request.with_user(self.employee1_user).action_confirm()
        self.assertTrue(approval_request.activity_search(['to_approvals.mail_act_approval'], self.team_leader_user_01.id))
        self.assertFalse(approval_request.activity_search(['to_approvals.mail_act_approval'], self.approval_officer_user_01.id))

        approval_request.with_user(self.team_leader_user_01).action_validate()
        self.assertFalse(approval_request.activity_search(['to_approvals.mail_act_approval'], self.team_leader_user_01.id))
        self.assertTrue(approval_request.activity_search(['to_approvals.mail_act_approval'], self.approval_officer_user_01.id))

        approval_request.with_user(self.approval_officer_user_01).action_validate()
        self.assertFalse(approval_request.activity_search(['to_approvals.mail_act_approval'], self.team_leader_user_01.id))
        self.assertFalse(approval_request.activity_search(['to_approvals.mail_act_approval'], self.approval_officer_user_01.id))

    def test_07_01_list_of_approvers_empty(self):
        """
         Case: Xác nhận yêu cầu phê duyệt khi không có người trong danh sách duyệt
         Output: Cảnh báo lỗi danh sách phê duyệt trống
        """
        type_empty_approvers = self.env['approval.request.type'].create({
            'name':'List of approvers is empty',
            'type':'generic',
            'manager_approval': 'none',
            'type_approval_user_line_ids': False
        })
        approval_request = self.env['approval.request'].with_user(self.employee1_user).create({
            'title':'Approval request',
            'approval_type_id': type_empty_approvers.id,
            'currency_id': self.env.company.currency_id.id,
            'employee_id': self.employee1_user.employee_id.id,
            'deadline': fields.Date.today()
            })
        with self.assertRaises(UserError):
            approval_request.with_user(self.employee1_user).action_confirm()
