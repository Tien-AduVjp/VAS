from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestPermissionKanban(Common):

    def test_01_check_permission_dragging_kanban_at_draft(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo chuyển -> xác nhận
            Expect: Thành công, trạng thái chuyển là xác nhận.
        """
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.assertEqual(self.approval_request.state, 'confirm')

    def test_02_check_permission_dragging_kanban_at_draft(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo chuyển -> được chấp nhận
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'validate'
            })

    def test_03_check_permission_dragging_kanban_at_draft(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'done'
            })

    def test_04_check_permission_dragging_kanban_at_draft(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'refuse'
            })

    def test_05_check_permission_dragging_kanban_at_draft(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo chuyển sang hủy bỏ
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'cancel'
            })

    def test_06_check_permission_dragging_kanban_at_confirm(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> đã chấp nhận
            Expect: Thành công, trạng thái chuyển là đã chấp nhận.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.assertEqual(self.approval_request.state, 'confirm')
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'validate'
            })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
                'state': 'validate'
            })
        self.assertEqual(self.approval_request.state, 'validate')

    def test_07_check_permission_dragging_kanban_at_confirm(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> đã từ chối.
            Expect: Thành công, trạng thái chuyển là đã từ chối.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'refuse'
            })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
                'state': 'refuse'
            })
        self.assertEqual(self.approval_request.state, 'refuse')

    def test_08_check_permission_dragging_kanban_at_confirm(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> hoàn thành
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'done'
            })

    def test_09_check_permission_dragging_kanban_at_confirm(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> dự thảo
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'draft'
            })

    def test_10_check_permission_dragging_kanban_at_confirm(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> hủy bỏ
            Expect: Thành công, đề nghị trình duyệt ở trạng thái hủy bỏ.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'cancel'
        })
        self.assertEqual(self.approval_request.state, 'cancel')

    def test_11_check_permission_dragging_kanban_at_validate(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> được phê duyệt -> hoàn thành
            Expect: Thành công, đề nghị trình duyệt ở trạng thái hoàn thành
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'validate'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'done'
        })
        self.assertEqual(self.approval_request.state, 'done')

    def test_12_check_permission_dragging_kanban_at_validate(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> được phê duyệt -> dự thảo
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'validate'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'draft'
            })
    def test_13_check_permission_dragging_kanban_at_validate(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> được phê duyệt -> xác nhận
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'validate'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'confirm'
            })
    def test_14_check_permission_dragging_kanban_at_validate(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> được phê duyệt -> từ chối
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'validate'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'refuse'
            })

    def test_15_check_permission_dragging_kanban_at_validate(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> được phê duyệt -> hủy bỏ
            Expect: Thành công, trình duyệt ở thạng thái hủy bỏ.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'validate'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'cancel'
        })
        self.assertEqual(self.approval_request.state, 'cancel')

    def test_16_check_permission_dragging_kanban_at_refuse(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> đã từ chối -> dự thảo
            Expect: Thông thành công, báo lỗi người dùng
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'refuse'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'draft'
            })

    def test_17_check_permission_dragging_kanban_at_refuse(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> đã từ chối -> xác nhận
            Expect: Thông thành công, báo lỗi người dùng
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'refuse'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'confirm'
            })

    def test_18_check_permission_dragging_kanban_at_refuse(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> đã từ chối -> đã chấp nhận
            Expect: Thông thành công, báo lỗi người dùng
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'refuse'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'validate'
            })

    def test_19_check_permission_dragging_kanban_at_refuse(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> đã từ chối -> hoàn thành
            Expect: Thông thành công, báo lỗi người dùng
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'refuse'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'done'
            })

    def test_20_check_permission_dragging_kanban_at_refuse(self):
        """
            Input: Yêu cầu ở trạng thái dự thảo -> xác nhận -> đã từ chối -> hủy bỏ
            Expect: Thành công, trình duyệt ở thạng thái hủy bỏ.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'refuse'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'cancel'
        })
        self.assertEqual(self.approval_request.state, 'cancel')

    def test_21_check_permission_dragging_kanban_at_done(self):
        """
            Input: chuyển thạng thái đề nghị trình duyệt từ hoàn thành -> dự thảo.
            Expect: Không thành công, báo lỗi ngưởi dùng
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'validate'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'done'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'draft'
            })

    def test_22_check_permission_dragging_kanban_at_done(self):
        """
            Input: chuyển thạng thái đề nghị trình duyệt từ hoàn thành -> xác nhận.
            Expect: Không thành công, báo lỗi ngưởi dùng
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'validate'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'done'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'confirm'
            })

    def test_23_check_permission_dragging_kanban_at_done(self):
        """
            Input: chuyển thạng thái đề nghị trình duyệt từ hoàn thành -> được chấp nhận.
            Expect: Không thành công, báo lỗi ngưởi dùng
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'validate'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'done'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'validate'
            })

    def test_24_check_permission_dragging_kanban_at_done(self):
        """
            Input: chuyển thạng thái đề nghị trình duyệt từ hoàn thành -> được từ chối.
            Expect: Không thành công, báo lỗi ngưởi dùng
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'validate'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'done'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'refuse'
            })

    def test_25_check_permission_dragging_kanban_at_done(self):
        """
            Input: chuyển thạng thái đề nghị trình duyệt từ hoàn thành -> hủy bỏ.
            Expect: Không thành công, báo lỗi ngưởi dùng
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).with_context(force_approval=True).write({
            'state': 'validate'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'done'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'cancel'
        })

    def test_26_check_permission_dragging_kanban_at_cancel(self):
        """
            Input: chuyển thạng thái đề nghị trình duyệt từ hủy bỏ -> dự thảo
            Expect: Thành công, trình duyệt ở trạng thái dự thảo.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'cancel'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'draft'
        })
        self.assertEqual(self.approval_request.state, 'draft')

    def test_27_check_permission_dragging_kanban_at_cancel(self):
        """
            Input: chuyển thạng thái đề nghị trình duyệt từ hủy bỏ -> xác nhận
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'cancel'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'confirm'
            })

    def test_28_check_permission_dragging_kanban_at_cancel(self):
        """
            Input: chuyển thạng thái đề nghị trình duyệt từ hủy bỏ -> được chấp nhận
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'cancel'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'validate'
            })

    def test_29_check_permission_dragging_kanban_at_cancel(self):
        """
            Input: chuyển thạng thái đề nghị trình duyệt từ hủy bỏ -> bị từ chối
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'cancel'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'refuse'
            })

    def test_30_check_permission_dragging_kanban_at_cancel(self):
        """
            Input: chuyển thạng thái đề nghị trình duyệt từ hủy bỏ -> hoàn thành
            Expect: Không thành công, báo lỗi người dùng.
        """
        self.approval_request.write({
            'approval_type_id': self.type_multiple_approvers.id
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'confirm'
        })
        self.approval_request.with_user(self.env.ref('base.user_admin')).write({
            'state': 'cancel'
        })
        with self.assertRaises(UserError):
            self.approval_request.with_user(self.env.ref('base.user_admin')).write({
                'state': 'done'
            })
