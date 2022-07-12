from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestPermissionKanban(Common):
    
    """
        Kiểm tra với kiểu phê duyệt: No Validation
        Nhân viên 1 tạo yêu cầu phê duyệt, kiểm tra quyền thay đổi trạng thái
    """
    def test_01_check_permission_dragging_kanban(self):
        # Case 1: Yêu cầu ở trạng thái dự thảo chuyển sang xác nhận -> Thành công
        self.approve_request_employee.with_user(self.user_employee_1).write({
            'state': 'confirm'
        })
        self.assertEqual(self.approve_request_employee.state, 'validate')

    def test_02_check_permission_dragging_kanban(self):
        # Case 2: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt lần 1 -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'validate1'
            })
    
    def test_03_check_permission_dragging_kanban(self):
        # Case 3: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt  -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'validate'
            })
    
    def test_04_check_permission_dragging_kanban(self):
        # Case 4: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành  -> Ngoại lệ trạng thái phải là đã phê duyệt
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'done'
            })
    
    def test_05_check_permission_dragging_kanban(self):
        # Case 5: Yêu cầu ở trạng thái đã phê duyệt chuyển sang hoàn thành -> Thành công
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'state': 'validate'
        })
        self.approve_request_employee.with_user(self.user_employee_1).write({
            'state': 'done'
        })
        self.assertEqual(self.approve_request_employee.state, 'done')
    
    def test_06_check_permission_dragging_kanban(self):
        # Case 6: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'refuse'
            })
            
    def test_07_check_permission_dragging_kanban(self):
        # Case 7: Yêu cầu ở trạng thái dự thảo chuyển sang huỷ -> Thành công
        self.approve_request_employee.with_user(self.user_employee_1).write({
            'state': 'cancel'
        })
        self.assertEqual(self.approve_request_employee.state, 'cancel')
        
    """
        Kiểm tra với kiểu phê duyệt: No Validation
        Quản lý của nhân viên 1, Kiểm tra quyền thay đổi trạng thái
    """
    def test_08_check_permission_dragging_kanban(self):
        # Case 1: Yêu cầu ở trạng thái dự thảo chuyển sang xác nhận -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'confirm'
            })

    def test_09_check_permission_dragging_kanban(self):
        # Case 2: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt lần 1 -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'validate1'
            })
    
    def test_10_check_permission_dragging_kanban(self):
        # Case 3: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'validate'
            })
    
    def test_11_check_permission_dragging_kanban(self):
        # Case 4: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'done'
            })
    
    def test_12_check_permission_dragging_kanban(self):
        # Case 5: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối  -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'refuse'
            })
    
    def test_13_check_permission_dragging_kanban(self):
        # Case 6: Yêu cầu ở trạng thái dự thảo chuyển sang huỷ -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'cancel'
            })
    
    """
        Kiểm tra với kiểu phê duyệt: No Validation
        Người dùng có Officer, Kiểm tra thay đổi trạng thái
    """
    def test_14_check_permission_dragging_kanban(self):
        # Case 1: Yêu cầu ở trạng thái dự thảo chuyển sang xác nhận -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'confirm'
            })

    def test_15_check_permission_dragging_kanban(self):
        # Case 2: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt lần 1 -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'validate1'
            })
    
    def test_16_check_permission_dragging_kanban(self):
        # Case 3: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'validate'
            })
    
    def test_17_check_permission_dragging_kanban(self):
        # Case 4: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'done'
            })
    
    def test_18_check_permission_dragging_kanban(self):
        # Case 5: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'refuse'
            })
    
    def test_19_check_permission_dragging_kanban(self):
        # Case 6: Yêu cầu ở trạng thái dự thảo chuyển sang huỷ -> Ngoại lệ không có quyền
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'cancel'
            })
            
    """
        Kiểm tra với kiểu phê duyệt: Manager
        Nhân viên 1 tạo yêu cầu phê duyệt, kiểm tra quyền thay đổi trạng thái
    """
    def test_20_check_permission_dragging_kanban(self):
        # Case 1: Yêu cầu ở trạng thái dự thảo chuyển sang xác nhận -> Thành công, trạng thái chuyển là xác nhận
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        self.approve_request_employee.with_user(self.user_employee_1).write({
            'state': 'confirm'
        })
        self.assertEqual(self.approve_request_employee.state, 'confirm')

    def test_21_check_permission_dragging_kanban(self):
        # Case 2: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt lần 1 -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'validate1'
            })
    
    def test_22_check_permission_dragging_kanban(self):
        # Case 3: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'validate'
            })
    
    def test_23_check_permission_dragging_kanban(self):
        # Case 4: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành  -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'done'
            })
    
    def test_24_check_permission_dragging_kanban(self):
        # Case 5: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối  -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'refuse'
            })
    
    def test_25_check_permission_dragging_kanban(self):
        # Case 6: Yêu cầu ở trạng thái dự thảo chuyển sang huỷ -> Thành công, trạng thái chuyển là huỷ
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        self.approve_request_employee.with_user(self.user_employee_1).write({
            'state': 'cancel'
        })
        self.assertEqual(self.approve_request_employee.state, 'cancel')
    
    """
        Kiểm tra với kiểu phê duyệt: Manager
        Quản lý của nhân viên 1, Kiểm tra quyền thay đổi trạng thái
    """
    def test_26_check_permission_dragging_kanban(self):
        # Case 1: Yêu cầu ở trạng thái dự thảo chuyển sang xác nhận -> Thành công, trạng thái  là xác nhận
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        self.approve_request_employee.with_user(self.user_manager).write({
            'state': 'confirm'
        })
        self.assertEqual(self.approve_request_employee.state, 'confirm')

    def test_27_check_permission_dragging_kanban(self):
        # Case 2: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt lần 1 -> Ngoại lệ trạng thái phải ở trạng thái đã xác nhận
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'validate1'
            })
    
    def test_28_check_permission_dragging_kanban(self):
        # Case 3: Yêu cầu ở trạng thái đã xác nhận chuyển sang phê duyệt lần 1 -> Thành công, yêu cầu chuyển trạng thái là đã phê duyệt
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_leader.id,
            'state': 'confirm'
        })
        self.approve_request_employee.with_user(self.user_manager).write({
            'state': 'validate1'
        })
        self.assertEqual(self.approve_request_employee.state, 'validate')
    
    def test_29_check_permission_dragging_kanban(self):
        # Case 4: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'validate'
            })
    
    def test_30_check_permission_dragging_kanban(self):
        # Case 5: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành  -> Ngoại lệ trạng thái phải ở đã phê duyệt
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'done'
            })
    
    def test_31_check_permission_dragging_kanban(self):
        # Case 6: Yêu cầu ở trạng thái đã phê duyệt chuyển sang hoàn thành  -> Thành công, yêu cầu chuyển trạng thái hoàn thành
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_leader.id,
            'state': 'validate'
        })
        self.approve_request_employee.with_user(self.user_manager).write({
            'state': 'done'
        })
        self.assertEqual(self.approve_request_employee.state, 'done')
    
    def test_32_check_permission_dragging_kanban(self):
        # Case 7: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối  -> Ngoại lệ phải ở trạng tháu xác nhận, phê duyệt lần , phê duyệt hoặc hoàn thành
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'refuse'
            })
            
    def test_33_check_permission_dragging_kanban(self):
        # Case 8: Yêu cầu ở trạng thái đã xác nhận chuyển sang từ chối -> Thành công, yêu cầu chuyển trạng thái là từ chối
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_leader.id,
            'state': 'confirm'
        })
        self.approve_request_employee.with_user(self.user_manager).write({
            'state': 'refuse'
        })
        self.assertEqual(self.approve_request_employee.state, 'refuse')
    
    def test_34_check_permission_dragging_kanban(self):
        # Case 9: Yêu cầu ở trạng thái dự thảo chuyển sang huỷ -> Thành công, trạng thái là huỷ
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        self.approve_request_employee.with_user(self.user_manager).write({
            'state': 'cancel'
        })
        self.assertEqual(self.approve_request_employee.state, 'cancel')
    
    """
        Kiểm tra với kiểu phê duyệt: Manager
        Người dùng có Officer, Kiểm tra thay đổi trạng thái
    """
    def test_35_check_permission_dragging_kanban(self):
        # Case 1: Yêu cầu ở trạng thái dự thảo chuyển sang xác nhận -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'confirm'
            })

    def test_36_check_permission_dragging_kanban(self):
        # Case 2: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt lần 1 -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'validate1'
            })
    
    def test_37_check_permission_dragging_kanban(self):
        # Case 3: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'validate'
            })
    
    def test_38_check_permission_dragging_kanban(self):
        # Case 4: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'done'
            })
    
    def test_39_check_permission_dragging_kanban(self):
        # Case 5: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối  -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'refuse'
            })
    
    def test_40_check_permission_dragging_kanban(self):
        # Case 6: Yêu cầu ở trạng thái dự thảo chuyển sang huỷ -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_leader.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'cancel'
            })
    
    """
        Kiểm tra với kiểu phê duyệt: Approval Officer
        Nhân viên 1 tạo yêu cầu phê duyệt, kiểm tra quyền thay đổi trạng thái
    """
    def test_41_check_permission_dragging_kanban(self):
        # Case 1: Yêu cầu ở trạng thái dự thảo chuyển sang xác nhận -> Thành công, trạng thái  là xác nhận
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        self.approve_request_employee.with_user(self.user_employee_1).write({
            'state': 'confirm'
        })
        self.assertEqual(self.approve_request_employee.state, 'confirm')

    def test_42_check_permission_dragging_kanban(self):
        # Case 2: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt lần 1 -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'validate1'
            })
    
    def test_43_check_permission_dragging_kanban(self):
        # Case 3: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'validate'
            })
    
    def test_44_check_permission_dragging_kanban(self):
        # Case 4: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'done'
            })
    
    def test_45_check_permission_dragging_kanban(self):
        # Case 5: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'refuse'
            })
    
    def test_46_check_permission_dragging_kanban(self):
        # Case 6: Yêu cầu ở trạng thái dự thảo chuyển sang huỷ -> Thành công, trạng thái là huỷ
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        self.approve_request_employee.with_user(self.user_employee_1).write({
            'state': 'cancel'
        })
        self.assertEqual(self.approve_request_employee.state, 'cancel')
    
    """
        Kiểm tra với kiểu phê duyệt: Approval Officer
        Quản lý của nhân viên 1, Kiểm tra quyền thay đổi trạng thái
    """
    def test_47_check_permission_dragging_kanban(self):
        # Case 1: Yêu cầu ở trạng thái dự thảo chuyển sang xác nhận -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'confirm'
            })

    def test_48_check_permission_dragging_kanban(self):
        # Case 2: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt lần 1 -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'validate1'
            })
    
    def test_49_check_permission_dragging_kanban(self):
        # Case 3: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'validate'
            })
    
    def test_50_check_permission_dragging_kanban(self):
        # Case 4: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'done'
            })
    
    def test_51_check_permission_dragging_kanban(self):
        # Case 5: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối  -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'refuse'
            })
    
    def test_52_check_permission_dragging_kanban(self):
        # Case 6: Yêu cầu ở trạng thái dự thảo chuyển sang huỷ -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'cancel'
            })
    
    """
        Kiểm tra với kiểu phê duyệt: Approval Officer
        Người dùng có Officer, Kiểm tra thay đổi trạng thái
    """
    def test_53_check_permission_dragging_kanban(self):
        # Case 1: Yêu cầu ở trạng thái dự thảo chuyển sang xác nhận -> Thành công, trạng thái chuyển là xác nhận
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        self.approve_request_employee.with_user(self.user_approve_officer).write({
            'state': 'confirm'
        })
        self.assertEqual(self.approve_request_employee.state, 'confirm')

    def test_54_check_permission_dragging_kanban(self):
        # Case 2: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt lần 1 -> Ngoại lệ trạng thái phải ở trạng thái đã xác nhận
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'validate1'
            })
    
    def test_55_check_permission_dragging_kanban(self):
        # Case 3: Yêu cầu ở trạng thái đã xác nhận chuyển sang phê duyệt lần 1 -> Thành công, yêu cầu chuyển trạng thái là đã phê duyệt
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_hr.id,
            'state': 'confirm'
        })
        self.approve_request_employee.with_user(self.user_approve_officer).write({
            'state': 'validate1'
        })
        self.assertEqual(self.approve_request_employee.state, 'validate')
    
    def test_56_check_permission_dragging_kanban(self):
        # Case 4: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'validate'
            })
    
    def test_57_check_permission_dragging_kanban(self):
        # Case 5: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành -> Ngoại lệ trạng thái phải ở đã phê duyệt
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'done'
            })
    
    def test_58_check_permission_dragging_kanban(self):
        # Case 6: Yêu cầu ở trạng thái đã phê duyệt chuyển sang hoàn thành -> Thành công, yêu cầu chuyển trạng thái là hoàn thành
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_hr.id,
            'state': 'validate'
        })
        self.approve_request_employee.with_user(self.user_approve_officer).write({
            'state': 'done'
        })
        self.assertEqual(self.approve_request_employee.state, 'done')
    
    def test_59_check_permission_dragging_kanban(self):
        # Case 7: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối -> Ngoại lệ phải ở trạng tháu xác nhận, phê duyệt lần , phê duyệt hoặc hoàn thành
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'refuse'
            })
    
    def test_60_check_permission_dragging_kanban(self):
        # Case 8: Yêu cầu ở trạng thái đã xác nhận chuyển sang từ chối -> Thành công, yêu cầu chuyển trạng thái là từ chối
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_hr.id,
            'state': 'confirm'
        })
        self.approve_request_employee.with_user(self.user_approve_officer).write({
            'state': 'refuse'
        })
        self.assertEqual(self.approve_request_employee.state, 'refuse')
    
    def test_61_check_permission_dragging_kanban(self):
        # Case 9: Yêu cầu ở trạng thái dự thảo chuyển sang huỷ -> Thành công, trạng thái là huỷ
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_hr.id
        })
        self.approve_request_employee.with_user(self.user_approve_officer).write({
            'state': 'cancel'
        })
        self.assertEqual(self.approve_request_employee.state, 'cancel')
        
    """
        Kiểm tra với kiểu phê duyệt: Manager and Approval Officer
        Nhân viên 1 tạo yêu cầu phê duyệt, kiểm tra quyền thay đổi trạng thái
    """
    def test_62_check_permission_dragging_kanban(self):
        # Case 1: Yêu cầu ở trạng thái dự thảo chuyển sang xác nhận -> Thành công, trạng thái  là xác nhận
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        self.approve_request_employee.with_user(self.user_employee_1).write({
            'state': 'confirm'
        })
        self.assertEqual(self.approve_request_employee.state, 'confirm')

    def test_63_check_permission_dragging_kanban(self):
        # Case 2: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt lần 1 -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'validate1'
            })
    
    def test_64_check_permission_dragging_kanban(self):
        # Case 3: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'validate'
            })
    
    def test_65_check_permission_dragging_kanban(self):
        # Case 4: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'done'
            })
    
    def test_66_check_permission_dragging_kanban(self):
        # Case 5: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).write({
                'state': 'refuse'
            })
    
    def test_67_check_permission_dragging_kanban(self):
        # Case 6: Yêu cầu ở trạng thái dự thảo chuyển sang huỷ -> Thành công, trạng thái là huỷ
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        self.approve_request_employee.with_user(self.user_employee_1).write({
            'state': 'cancel'
        })
        self.assertEqual(self.approve_request_employee.state, 'cancel')
    
    """
        Kiểm tra với kiểu phê duyệt: Manager and Approval Officer
        Quản lý của nhân viên 1, Kiểm tra quyền thay đổi trạng thái
    """
    def test_68_check_permission_dragging_kanban(self):
        # Case 1: Yêu cầu ở trạng thái dự thảo chuyển sang xác nhận -> Thành công, yêu cầu chuyển trạng thái là đã xác nhận
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        self.approve_request_employee.with_user(self.user_manager).write({
            'state': 'confirm'
        })
        self.assertEqual(self.approve_request_employee.state, 'confirm')
    
    def test_69_check_permission_dragging_kanban(self):
        # Case 2: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt lần 1 -> Ngoại lệ, yêu cầu phải ở trạng thái đã xác nhận
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'validate1'
            })
    
    def test_70_check_permission_dragging_kanban(self):
        # Case 3: Yêu cầu ở trạng thái đã xác nhận chuyển sang phê duyệt lần 1 -> Thành công, yêu cầu chuyển trạng thái là phê duyệt lần 1
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_both.id,
            'state': 'confirm'
        })
        self.approve_request_employee.with_user(self.user_manager).write({
            'state': 'validate1'
        })
        self.assertEqual(self.approve_request_employee.state, 'validate1')
    
    def test_71_check_permission_dragging_kanban(self):
        # Case 4: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id,
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'validate'
            })
    
    def test_72_check_permission_dragging_kanban(self):
        # Case 5: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'done'
            })
    
    def test_73_check_permission_dragging_kanban(self):
        # Case 6: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).write({
                'state': 'refuse'
            })
    
    def test_74_check_permission_dragging_kanban(self):
        # Case 7: Yêu cầu ở trạng thái đã xác nhận chuyển sang từ chối -> Thành công, yêu cầu chuyển trạng thái là từ chối
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_both.id,
            'state': 'confirm'
        })
        self.approve_request_employee.with_user(self.user_manager).write({
            'state': 'refuse'
        })
        self.assertEqual(self.approve_request_employee.state, 'refuse')
    
    def test_75_check_permission_dragging_kanban(self):
        # Case 8: Yêu cầu ở trạng thái dự thảo chuyển sang huỷ -> Ngoại lệ không có quyền
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        self.approve_request_employee.with_user(self.user_manager).write({
            'state': 'cancel'
        })
    
    """
        Kiểm tra với kiểu phê duyệt: Approval Officer
        Người dùng có Officer, Kiểm tra thay đổi trạng thái
    """
    def test_76_check_permission_dragging_kanban(self):
        # Case 1: Yêu cầu ở trạng thái dự thảo chuyển sang xác nhận -> Thành công, trạng thái  là xác nhận
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        self.approve_request_employee.with_user(self.user_approve_officer).write({
            'state': 'confirm'
        })
        self.assertEqual(self.approve_request_employee.state, 'confirm')
    
    def test_77_check_permission_dragging_kanban(self):
        # Case 2: Yêu cầu ở trạng thái dự thảo chuyển sang phê duyệt lần 1 -> Ngoại lệ trạng thái phải ở trạng thái đã xác nhận
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'validate1'
            })
    
    def test_78_check_permission_dragging_kanban(self):
        # Case 3: Yêu cầu ở trạng thái đã xác nhận chuyển sang phê duyệt lần 1 -> Thành công, yêu cầu chuyển trạng thái là đã phê duyệt
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_both.id,
            'state': 'confirm'
        })
        self.approve_request_employee.with_user(self.user_approve_officer).write({
            'state': 'validate1'
        })
        self.assertEqual(self.approve_request_employee.state, 'validate')
    
    def test_79_check_permission_dragging_kanban(self):
        # Case 4: Yêu cầu ở trạng thái dự thảo chuyển sang đã phê duyệt -> Ngoại lệ yêu cầu phải ở trạng thái phê duyệt lần 1
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'validate'
            })
    
    def test_80_check_permission_dragging_kanban(self):
        # Case 5: Yêu cầu ở trạng thái phê duyệt lần 1 chuyển sang đã phê duyệt -> Thành công, yêu cầu chuyển trạng thái là đã phê duyệt
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_both.id,
            'state': 'validate1'
        })
        self.approve_request_employee.with_user(self.user_approve_officer).write({
            'state': 'validate'
        })
        self.assertEqual(self.approve_request_employee.state, 'validate')
    
    def test_81_check_permission_dragging_kanban(self):
        # Case 6: Yêu cầu ở trạng thái dự thảo chuyển sang hoàn thành-> Ngoại lệ trạng thái phải ở đã phê duyệt
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'done'
            })
    
    def test_82_check_permission_dragging_kanban(self):
        # Case 7: Yêu cầu ở trạng thái đã phê duyệt chuyển sang hoàn thành  -> Thành công, yêu cầu chuyển trạng thái là đã hoàn thành
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_both.id,
            'state': 'validate'
        })
        self.approve_request_employee.with_user(self.user_approve_officer).write({
            'state': 'done'
        })
        self.assertEqual(self.approve_request_employee.state, 'done')
    
    def test_83_check_permission_dragging_kanban(self):
        # Case 8: Yêu cầu ở trạng thái dự thảo chuyển sang từ chối -> Ngoại lệ phải ở trạng thái xác nhận, phê duyệt lần , phê duyệt hoặc hoàn thành
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).write({
                'state': 'refuse'
            })
    
    def test_84_check_permission_dragging_kanban(self):
        # Case 9: Yêu cầu ở trạng thái đã xác nhận chuyển sang từ chối -> Thành công, yêu cầu chuyển trạng thái là từ chối
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_both.id,
            'state': 'confirm'
        })
        self.approve_request_employee.with_user(self.user_approve_officer).write({
            'state': 'refuse'
        })
        self.assertEqual(self.approve_request_employee.state, 'refuse')
    
    def test_85_check_permission_dragging_kanban(self):
        # Case 10: Yêu cầu ở trạng thái dự thảo chuyển sang huỷ -> Thành công, trạng thái là huỷ
        self.approve_request_employee.write({
            'approval_type_id': self.approve_type_both.id
        })
        self.approve_request_employee.with_user(self.user_approve_officer).write({
            'state': 'cancel'
        })
        self.assertEqual(self.approve_request_employee.state, 'cancel')
