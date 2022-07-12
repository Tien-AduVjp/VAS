from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo import fields

from . import common


@tagged('post_install', '-at_install')
class TestApprovalAccessRight(common.Common):

    def test_02_01_can_confirm(self):
        """
            [Test case] Kiểm tra quyền có thể xác nhận đề nghị trình duyệt.
            Input: Người dùng hiện tại nằm trong danh sách người duyệt và là quản lý của người gửi đề nghị trình duyệt.
            Expect: Không thể xác nhận đề nghị trình duyệt.
        """
        self.assertTrue(self.approval_request.with_user(self.team_leader_user_01).can_confirm)

    def test_02_02_can_confirm(self):
        """
            [Test case] Kiểm tra quyền có thể xác nhận đề nghị trình duyệt.
            Input: Người dùng hiện tại nằm trong danh sách phê duyệt, có quyền cán bộ phê duyệt.
            Expect: Không thể xác nhận đề nghị trình duyệt.
        """
        self.assertFalse(self.approval_request.with_user(self.approval_officer_user_01).can_confirm)

    def test_02_03_can_confirm(self):
        """
            [Test case] Kiểm tra quyền có thể xác nhận đề nghị trình duyệt.
            Input: Người dùng hiện tại là quản lý phê duyệt, không nằm trong danh sách người duyệt.
            Expect: Có thể xác nhận đề nghị trình duyệt.
        """
        self.assertTrue(self.approval_request.with_user(self.env.ref('base.user_admin')).can_confirm)

    def test_02_04_can_confirm(self):
        """
            [Test case] Kiểm tra quyền có thể xác nhận đề nghị trình duyệt.
            Input: Người dùng hiện tại là người gửi đề nghị trình duyệt.
            Expect: Có thể xác nhận đề nghị trình duyệt.
        """
        self.assertTrue(self.approval_request.with_user(self.employee1_user).can_confirm)

    def test_03_01_admin_can_force_validate(self):
        self.approval_request.with_user(self.employee1_user).action_confirm()
        approval_request = self.approval_request.with_user(self.env.ref('base.user_admin'))
        self.assertTrue(approval_request.can_force_validate)

    def test_03_01_can_validate_can_refuse(self):
        """
            [Test case] Kiểm tra quyền có thể xác nhận hoặc từ chối đề nghị trình duyệt thuộc kiểu duyệt có thứ tự.
            Input: Người dùng hiện tại có quyền quản lý phê duyệt.
            Expect: Có thể chấp nhận hoặc từ chối đề nghị trình duyệt.
        """
        self.approval_request.with_user(self.employee1_user).action_confirm()

        approval_request = self.approval_request.with_user(self.approval_request.request_approval_user_line_ids[0].user_id)
        self.assertTrue(approval_request.can_validate)
        self.assertTrue(approval_request.can_refuse)

    def test_03_02_can_validate_can_refuse(self):
        """
            [Test case] Kiểm tra quyền có thể xác nhận hoặc từ chối đề nghị trình duyệt thuộc kiểu duyệt có thứ tự.
            Input: Người dùng cos thứ tự duyệt thứ 2
            Expect: Không được duyệt / từ chối
        """
        self.approval_request.with_user(self.employee1_user).action_confirm()

        approval_request = self.approval_request.with_user(self.approval_request.request_approval_user_line_ids[1].user_id)
        self.assertFalse(approval_request.can_validate)
        self.assertFalse(approval_request.can_refuse)
        with self.assertRaises(UserError):
            approval_request.action_validate()
        with self.assertRaises(UserError):
            approval_request.action_refuse()
        approval_request.with_user(self.approval_request.request_approval_user_line_ids[0].user_id).action_validate()
        try:
            approval_request.action_refuse()
        except Exception:
            self.fail("%s should be able to refuse." % self.approval_request.request_approval_user_line_ids[1].user_id.name)

    def test_03_03_can_validate_can_refuse(self):
        """
            [Test case] Kiểm tra quyền có thể xác nhận hoặc từ chối đề nghị trình duyệt thuộc kiểu duyệt có thứ tự.
            Input: Người dùng hiện tại là người tiếp theo phê duyệt trong danh sách người phê duyệt.
            Expect: Có thể chấp nhận hoặc từ chối đề nghị trình duyệt.
        """
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.assertEqual(self.approval_request.next_approver_id, self.team_leader_user_01)
        self.assertTrue(self.approval_request.with_user(self.team_leader_user_01).can_validate)
        self.assertTrue(self.approval_request.with_user(self.team_leader_user_01).can_refuse)

    def test_03_03_compute_can_validate_can_refuse(self):
        """
            [Test case] Kiểm tra quyền có thể xác nhận hoặc từ chối đề nghị trình duyệt thuộc kiểu duyệt có thứ tự.
            Input: Người dùng hiện tại nằm trong danh sách phê duyệt nhưng không phải người duyệt kế tiếp.
            Expect: Không thể chấp nhận hoặc từ chối đề nghị trình duyệt.
        """
        self.assertFalse(self.approval_request.with_user(self.approval_officer_user_01).can_validate)
        self.assertFalse(self.approval_request.with_user(self.approval_officer_user_01).can_refuse)

    def test_03_04_compute_can_validate_can_refuse(self):
        """
            [Test case] Kiểm tra quyền có thể xác nhận hoặc từ chối đề nghị trình duyệt thuộc kiểu duyệt có thứ tự.
            Input: Người dùng hiện tại nằm trong danh sách phê duyệt nhưng không phải người duyệt kế tiếp.
            Expect: Không thể chấp nhận hoặc từ chối đề nghị trình duyệt.
        """
        approval_request = self.approval_request.with_user(self.approval_officer_user_02)
        self.assertFalse(approval_request.can_validate)
        self.assertFalse(approval_request.can_refuse)

    def test_03_04_compute_can_validate_can_refuse_1(self):
        """
            [Test case] Kiểm tra quyền có thể xác nhận hoặc từ chối đề nghị trình duyệt thuộc kiểu duyệt không có thứ tự.
            Input: Người dùng hiện tại nằm trong danh sách phê duyệt
            Expect: Có thể chấp nhận hoặc từ chối đề nghị trình duyệt
        """
        self.approval_request_01.action_confirm()
        # direct manager without team approval rights
        approval_request_01 = self.approval_request_01.with_user(self.employee2_user)
        try:
            approval_request_01.with_user(self.employee2_user).read(['name'])
        except Exception:
            self.fail("Employee 2 should be able to read his subordinates' requests")
        self.assertFalse(approval_request_01.can_validate)
        self.assertFalse(approval_request_01.can_refuse)
        # indirect manager having team approval rights
        approval_request_01 = self.approval_request_01.with_user(self.team_leader_user_01)
        self.assertTrue(approval_request_01.can_validate)
        self.assertTrue(approval_request_01.can_refuse)
        # department manager
        approval_request_01 = approval_request_01.with_user(self.department_manager_user_01)
        self.assertFalse(approval_request_01.can_validate)
        self.assertFalse(approval_request_01.can_refuse)
        # parent department manager
        approval_request_01 = approval_request_01.with_user(self.parent_department_manager_user_01)
        self.assertFalse(approval_request_01.can_validate)
        self.assertFalse(approval_request_01.can_refuse)
        # approval officer
        approval_request_01 = approval_request_01.with_user(self.approval_officer_user_01)
        self.assertTrue(approval_request_01.can_validate)
        self.assertTrue(approval_request_01.can_refuse)

    def test_04_01_compute_can_mark_done(self):
        """
            [Test case] Kiểm tra quyền có thể đánh dấu hoàn thành đề nghị trình duyệt.
            Input: Người dùng hiện tại nằm trong danh sách phê duyệt và là quản lý của người gưi đề nghị trình duyệt
            Expect: Có thể chuyển trạng thái đề nghị trình duyệt sang hoàn thành.
        """
        self.approval_request.action_confirm()
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).action_validate()
        self.assertTrue(self.approval_request.with_user(self.team_leader_user_01).can_done)
        self.approval_request.with_user(self.team_leader_user_01).action_done()

    def test_04_02_compute_can_mark_done(self):
        """
            [Test case] Kiểm tra quyền có thể đánh dấu hoàn thành đề nghị trình duyệt.
            Input: Người dùng hiện tại là quản lý trình duyệt.
            Expect: Có thể chuyển trạng thái đề nghị trình duyệt sang hoàn thành.
        """
        self.approval_request.action_confirm()
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).action_validate()
        self.assertTrue(self.approval_request.with_user(self.env.ref('base.user_admin')).can_done)
        self.approval_request.with_user(self.env.ref('base.user_admin')).action_done()

    def test_04_03_compute_can_mark_done(self):
        """
            [Test case] Kiểm tra quyền có thể đánh dấu hoàn thành đề nghị trình duyệt.
            Input: Người dùng hiện tại người gửi yêu cầu trình duyệt.
            Expect: Không thể chuyển
        """
        self.approval_request.action_confirm()
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).action_validate()
        self.assertTrue(self.approval_request.with_user(self.employee1_user).can_done)
        self.approval_request.with_user(self.employee1_user).action_done()

    def test_05_01_access_right_approval_request_base_user(self):
        self.assertTrue(self.env['approval.request'].with_user(self.employee1_user).check_access_rights('read'))
        self.assertTrue(self.env['approval.request'].with_user(self.employee1_user).check_access_rights('write'))
        self.assertTrue(self.env['approval.request'].with_user(self.employee1_user).check_access_rights('create'))
        self.assertTrue(self.env['approval.request'].with_user(self.employee1_user).check_access_rights('unlink'))

    def test_05_02_access_right_approval_request_approval_officer(self):
        self.assertTrue(self.env['approval.request'].with_user(self.approval_officer_user_01).check_access_rights('read'))
        self.assertTrue(self.env['approval.request'].with_user(self.approval_officer_user_01).check_access_rights('write'))
        self.assertTrue(self.env['approval.request'].with_user(self.approval_officer_user_01).check_access_rights('create'))
        self.assertTrue(self.env['approval.request'].with_user(self.approval_officer_user_01).check_access_rights('unlink'))

    def test_05_03_access_right_approval_request_type_base_user(self):
        self.assertTrue(self.env['approval.request.type'].with_user(self.employee1_user).check_access_rights('read'))
        with self.assertRaises(AccessError):
            self.env['approval.request.type'].with_user(self.employee1_user).check_access_rights('write')
        with self.assertRaises(AccessError):
            self.env['approval.request.type'].with_user(self.employee1_user).check_access_rights('create')
        with self.assertRaises(AccessError):
            self.env['approval.request.type'].with_user(self.employee1_user).check_access_rights('unlink')

    def test_05_04_access_right_approval_request_type_approval_officer(self):
        self.assertTrue(self.env['approval.request.type'].with_user(self.approval_officer_user_01).check_access_rights('read'))
        with self.assertRaises(AccessError):
            self.env['approval.request.type'].with_user(self.approval_officer_user_01).check_access_rights('write')
        with self.assertRaises(AccessError):
            self.env['approval.request.type'].with_user(self.approval_officer_user_01).check_access_rights('create')
        with self.assertRaises(AccessError):
            self.env['approval.request.type'].with_user(self.approval_officer_user_01).check_access_rights('unlink')

    def test_05_05_access_right_approval_request_type_approval_admin(self):
        self.assertTrue(self.env['approval.request.type'].with_user(self.env.ref('base.user_admin')).check_access_rights('read'))
        self.assertTrue(self.env['approval.request.type'].with_user(self.env.ref('base.user_admin')).check_access_rights('write'))
        self.assertTrue(self.env['approval.request.type'].with_user(self.env.ref('base.user_admin')).check_access_rights('create'))
        self.assertTrue(self.env['approval.request.type'].with_user(self.env.ref('base.user_admin')).check_access_rights('unlink'))

    def test_05_06_access_right_type_approval_user_line_base_user(self):
        self.assertTrue(self.env['approval.request.type'].with_user(self.employee1_user).check_access_rights('read'))
        with self.assertRaises(AccessError):
            self.env['approval.request.type'].with_user(self.employee1_user).check_access_rights('write')
        with self.assertRaises(AccessError):
            self.env['approval.request.type'].with_user(self.employee1_user).check_access_rights('create')
        with self.assertRaises(AccessError):
            self.env['approval.request.type'].with_user(self.employee1_user).check_access_rights('unlink')

    def test_05_07_access_right_type_approval_user_line_approval_manager(self):
        self.assertTrue(self.env['approval.request.type'].with_user(self.env.ref('base.user_admin')).check_access_rights('read'))
        self.assertTrue(self.env['approval.request.type'].with_user(self.env.ref('base.user_admin')).check_access_rights('write'))
        self.assertTrue(self.env['approval.request.type'].with_user(self.env.ref('base.user_admin')).check_access_rights('create'))
        self.assertTrue(self.env['approval.request.type'].with_user(self.env.ref('base.user_admin')).check_access_rights('unlink'))

    def test_05_08_access_right_request_approval_user_line_base_user(self):
        self.assertTrue(self.env['request.approval.user.line'].with_user(self.employee1_user).check_access_rights('read'))
        with self.assertRaises(AccessError):
            self.env['request.approval.user.line'].with_user(self.employee1_user).check_access_rights('write')
        with self.assertRaises(AccessError):
            self.env['request.approval.user.line'].with_user(self.employee1_user).check_access_rights('create')
        with self.assertRaises(AccessError):
            self.env['request.approval.user.line'].with_user(self.employee1_user).check_access_rights('unlink')

    def test_05_09_access_right_request_approval_user_line_approval_officer(self):
        self.assertTrue(self.env['request.approval.user.line'].with_user(self.approval_officer_user_01).check_access_rights('read'))
        with self.assertRaises(AccessError):
            self.env['request.approval.user.line'].with_user(self.approval_officer_user_01).check_access_rights('write')
        with self.assertRaises(AccessError):
            self.env['request.approval.user.line'].with_user(self.approval_officer_user_01).check_access_rights('create')
        with self.assertRaises(AccessError):
            self.env['request.approval.user.line'].with_user(self.approval_officer_user_01).check_access_rights('unlink')

    def test_05_10_access_right_request_approval_user_line_approval_officer(self):
        self.assertTrue(self.env['request.approval.user.line'].with_user(self.env.ref('base.user_admin')).check_access_rights('read'))
        self.assertTrue(self.env['request.approval.user.line'].with_user(self.env.ref('base.user_admin')).check_access_rights('write'))
        self.assertTrue(self.env['request.approval.user.line'].with_user(self.env.ref('base.user_admin')).check_access_rights('create'))
        self.assertTrue(self.env['request.approval.user.line'].with_user(self.env.ref('base.user_admin')).check_access_rights('unlink'))

    def test_06_01_access_rule_approval_request_base_user(self):
        """
            Người dùng thông thường không thể xem hay tương tác với trình duyệt của người khác.
        """
        with self.assertRaises(AccessError):
            self.approval_request.with_user(self.env.ref('base.user_demo')).check_access_rule('read')
        with self.assertRaises(AccessError):
            self.approval_request.with_user(self.env.ref('base.user_demo')).check_access_rule('write')
        with self.assertRaises(AccessError):
            self.approval_request.with_user(self.env.ref('base.user_demo')).check_access_rule('create')
        with self.assertRaises(AccessError):
            self.approval_request.with_user(self.env.ref('base.user_demo')).check_access_rule('unlink')

    def test_06_02_access_rule_approval_request_follower(self):
        """
            Người dùng thông thường được thêm vào danh sách theo dõi trong đề nghị có thể xem nhưng không thể sửa hay xóa.
        """
        self.approval_request.message_subscribe(partner_ids=self.env.ref('base.user_demo').employee_id.user_id.partner_id.ids)
        self.approval_request.with_user(self.env.ref('base.user_demo')).check_access_rule('read')
        with self.assertRaises(AccessError):
            self.approval_request.with_user(self.env.ref('base.user_demo')).check_access_rule('write')
        with self.assertRaises(AccessError):
            self.approval_request.with_user(self.env.ref('base.user_demo')).check_access_rule('create')
        with self.assertRaises(AccessError):
            self.approval_request.with_user(self.env.ref('base.user_demo')).check_access_rule('unlink')

    def test_06_03_access_rule_approval_request_parent(self):
        self.approval_request.with_user(self.employee1_user).action_confirm()
        self.approval_request.with_user(self.team_leader_user_01).check_access_rule('read')
        with self.assertRaises(AccessError):
            self.approval_request.with_user(self.team_leader_user_01).check_access_rule('write')
        with self.assertRaises(AccessError):
            self.approval_request.with_user(self.team_leader_user_01).check_access_rule('create')
        with self.assertRaises(AccessError):
            self.approval_request.with_user(self.team_leader_user_01).check_access_rule('unlink')

    def test_06_04_access_rule_approval_officer(self):
        """
            Người dùng thuộc nhóm quản lý phê duyệt có có toàn quyền với một đề nghị trình duyệt.
        """
        self.approval_request.with_user(self.env.ref('base.user_admin')).check_access_rule('read')
        self.approval_request.with_user(self.env.ref('base.user_admin')).check_access_rule('write')
        self.approval_request.with_user(self.env.ref('base.user_admin')).check_access_rule('create')
        self.approval_request.with_user(self.env.ref('base.user_admin')).check_access_rule('unlink')

    def test_06_05_access_rule_request_approval_user_line(self):
        """
            Người dùng thuộc nhóm người dùng thông thường chỉ có thể xem, không thể sửa hay xóa danh sách người phê duyệt.
        """
        self.approval_request.request_approval_user_line_ids.with_user(self.employee1_user).check_access_rule('read')
        with self.assertRaises(AccessError):
            self.approval_request.request_approval_user_line_ids[0].with_user(self.employee1_user).check_access_rights('write')
        with self.assertRaises(AccessError):
            self.approval_request.request_approval_user_line_ids.with_user(self.employee1_user).check_access_rights('create')
        with self.assertRaises(AccessError):
            self.approval_request.request_approval_user_line_ids.with_user(self.employee1_user).check_access_rights('unlink')

    def test_06_06_access_rule_request_approval_user_line(self):
        """
            Người dùng thuộc nhóm người dùng cán bộ có thể xem, và sửa thông tin người duyệt của chính họ nhưng không thể sửa thông tin của người khác
        """
        self.approval_request.request_approval_user_line_ids.with_user(self.approval_officer_user_01).check_access_rule('read')
        self.approval_request.request_approval_user_line_ids[1].with_user(self.approval_officer_user_01).check_access_rule('write')
        with self.assertRaises(AccessError):
            self.approval_request.request_approval_user_line_ids[0].with_user(self.approval_officer_user_01).check_access_rights('write')
        with self.assertRaises(AccessError):
            self.approval_request.request_approval_user_line_ids[0].with_user(self.approval_officer_user_01).unlink()

    def test_06_07_access_rule_request_approval_user_line(self):
        """
            Người dùng thuộc nhóm người dùng quản lý phê duyệt có toàn quyền với danh sách người phê duyệt
        """
        self.approval_request.request_approval_user_line_ids.with_user(self.approval_officer_user_01).check_access_rule('read')
        self.approval_request.request_approval_user_line_ids.with_user(self.env.ref('base.user_admin')).check_access_rule('write')
        self.approval_request.request_approval_user_line_ids.with_user(self.env.ref('base.user_admin')).check_access_rule('create')
        self.approval_request.request_approval_user_line_ids.with_user(self.env.ref('base.user_admin')).unlink()

    def test_06_08_access_rule_request_approval_user_line(self):
        """
            Quản lý của nhân viên trong danh sách phê duyệt chỉ có thể xem trình duyệt ở trạng thái khác dự thảo
            Nếu trình duyệt thuộc kiểu duyệt có thứ tự thì người duyệt tiếp theo mới có thể xem và chỉnh sửa trình duyệt.
        """
        try:
            self.approval_request.with_user(self.team_leader_user_01).check_access_rule('read')
        except Exception:
            self.fail("Team leader should be able to read request")
        with self.assertRaises(AccessError):
            self.approval_request.with_user(self.team_leader_user_01).check_access_rule('write')
        try:
            self.approval_request.with_user(self.approval_officer_user_01).check_access_rule('read')
        except Exception:
            self.fail("Approval Officer should be able to read request")
        try:
            for manager in self.employee1.parent_ids.user_id:
                self.approval_request.with_user(manager).check_access_rule('read')
        except Exception:
            self.fail("All managers should be able to read request")

    def test_07_01_personal_request(self):
        """
            Kiểm tra quyền người dùng nội bộ chỉ có thể tạo đề nghị trình duyệt cho mình, không thể tạo cho người khác.
        """
        with self.assertRaises(AccessError):
            self.env['approval.request'].with_user(self.employee1_user).create({
                'title':'Approval request',
                'approval_type_id': self.type_multiple_approvers.id,
                'currency_id': self.env.company.currency_id.id,
                'employee_id': self.employee2_user.employee_id.id,
                'deadline': fields.Date.today()
                })
