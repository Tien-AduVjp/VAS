from odoo.exceptions import AccessError
from odoo.tests.common import tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestAccessRights(Common):
    
    def test_01_access_rights_approve_request_type(self):
        # User access right
        self.approve_type_no_valid.with_user(self.user_employee_1).read()
        with self.assertRaises(AccessError):
            approve_type = self.env['approval.request.type'].with_user(self.user_employee_1).create({
                                'name': 'Demo'
                            })
        with self.assertRaises(AccessError):
            self.approve_type_no_valid.with_user(self.user_employee_1).write({'name': 'Demo'})
        with self.assertRaises(AccessError):
            self.approve_type_no_valid.with_user(self.user_employee_1).unlink()
        
        # Approve Officer access right 
        self.approve_type_no_valid.with_user(self.user_approve_officer).read()
        with self.assertRaises(AccessError):
            approve_type = self.env['approval.request.type'].with_user(self.user_approve_officer).create({
                                'name': 'Demo'
                            })
        with self.assertRaises(AccessError):
            self.approve_type_no_valid.with_user(self.user_approve_officer).write({'name': 'Demo'})
        with self.assertRaises(AccessError):
            self.approve_type_no_valid.with_user(self.user_approve_officer).unlink()
            
        # Approve Administrator access right
        approve_type = self.env['approval.request.type'].with_user(self.user_approve_admin).create({
                            'name': 'Demo'
                        })
        approve_type.with_user(self.user_approve_admin).read()
        approve_type.with_user(self.user_approve_admin).write({'name': 'Demo 1'})
        approve_type.with_user(self.user_approve_admin).unlink()
        
    def test_02_access_right_approve_request(self):
        # User access right
        approve_request_user = self.env['approval.request'].with_user(self.user_employee_1).create({
                                    'title': 'Demo User',
                                    'approval_type_id': self.approve_type_no_valid.id,
                                    'employee_id': self.employee_1.id
                                })
        approve_request_user.with_user(self.user_employee_1).read()
        approve_request_user.with_user(self.user_employee_1).write({'title': 'Demo 1'})
        approve_request_user.with_user(self.user_employee_1).unlink()
        
        # Approve Officer access right 
        approve_request_officer = self.env['approval.request'].with_user(self.user_approve_officer).create({
                                    'title': 'Demo Officer',
                                    'approval_type_id': self.approve_type_no_valid.id,
                                    'employee_id': self.employee_approve_officer.id
                                })
        approve_request_officer.with_user(self.user_approve_officer).read()
        approve_request_officer.with_user(self.user_approve_officer).write({'title': 'Demo 2'})
        approve_request_officer.with_user(self.user_approve_officer).unlink()
            
        # Approve Administrator access right
        approve_request_admin = self.env['approval.request'].with_user(self.user_approve_admin).create({
                                    'title': 'Demo Administrator',
                                    'approval_type_id': self.approve_type_no_valid.id,
                                    'employee_id': self.employee_approve_admin.id
                                })
        approve_request_admin.with_user(self.user_approve_admin).read()
        approve_request_admin.with_user(self.user_approve_admin).write({'title': 'Demo 3'})
        approve_request_admin.with_user(self.user_approve_admin).unlink()
        
    def test_03_multi_company(self):
        approve_request_employee = self.env['approval.request'].with_user(self.user_employee_1).create({
                                    'title': 'Demo 1',
                                    'approval_type_id': self.approve_type_no_valid.id,
                                    'employee_id': self.employee_1.id
                                })
        # Users in other companies do not have access to the current company's records without permission
        with self.assertRaises(AccessError):
            approve_request_employee.with_user(self.user_admin_company_a).read()
        
        #Users in other companies have access to the current company's records when authorized
        self.user_admin_company_a.write({'company_ids': [(4, self.env.company.id, 0)]})
        approve_request_employee.with_user(self.user_admin_company_a).read()
    
    """
        Case: Employees only have internal user rights
    """
    def test_04_employee_rights_with_request(self):
    # Employee has full rights to his/her recording
        self.approve_request_employee.with_user(self.user_employee_1).check_access_rule('read')
        self.approve_request_employee.with_user(self.user_employee_1).check_access_rule('write')
        self.approve_request_employee.with_user(self.user_employee_1).check_access_rule('create')
        self.approve_request_employee.with_user(self.user_employee_1).check_access_rule('unlink')
    
    def test_05_employee_rights_with_request(self):
    # Employees have the right to read and edit the records of direct or indirect subordinates
        # 1: Direct subordinates
        self.approve_request_employee.with_user(self.user_manager).check_access_rule('read')
        self.approve_request_employee.with_user(self.user_manager).check_access_rule('write')
        with self.assertRaises(AccessError):
            self.approve_request_employee.with_user(self.user_manager).check_access_rule('create')
        with self.assertRaises(AccessError):
            self.approve_request_employee.with_user(self.user_manager).check_access_rule('unlink')
    
        # 2: Indirect subordinates
        self.approve_request_employee_2.with_user(self.user_manager).check_access_rule('read')
        self.approve_request_employee_2.with_user(self.user_manager).check_access_rule('write')
        with self.assertRaises(AccessError):
            self.approve_request_employee_2.with_user(self.user_manager).check_access_rule('create')
        with self.assertRaises(AccessError):
            self.approve_request_employee_2.with_user(self.user_manager).check_access_rule('unlink')

    def test_06_employee_rights_with_request(self):
    # Employees have the right to read other people's logs only when they are follow (not subordinates)
    
        # 1: Do not follow
        with self.assertRaises(AccessError):
            self.approve_request_employee_3.with_user(self.user_manager).check_access_rule('read')
        # 2: Follow
        self.approve_request_employee_3.message_subscribe(partner_ids=self.user_manager.partner_id.ids)
        self.approve_request_employee_3.with_user(self.user_manager).check_access_rule('read')
        with self.assertRaises(AccessError):
            self.approve_request_employee_3.with_user(self.user_manager).check_access_rule('write')
        with self.assertRaises(AccessError):
            self.approve_request_employee_3.with_user(self.user_manager).check_access_rule('create')
        with self.assertRaises(AccessError):
            self.approve_request_employee_3.with_user(self.user_manager).check_access_rule('unlink')
        
    def test_07_employee_rights_with_request(self):
    # Employees who are managers have the right to approve all requests of direct and indirect subordinates (Type: Manager)
        self.approve_request_employee.write({'approval_type_id': self.approve_type_leader.id})
        self.approve_request_employee_2.write({'approval_type_id': self.approve_type_leader.id})
        # 1: Direct subordinates
        self.assertTrue(self.approve_request_employee.with_user(self.user_manager).can_approve)
        # 2: Indirect subordinates
        self.assertTrue(self.approve_request_employee_2.with_user(self.user_manager).can_approve)
        
    def test_08_employee_rights_with_request(self):
    # Employees who are managers have the right to first approve requests of direct and indirect subordinates (Type: Manager and Approval Officer)
        self.approve_request_employee.write({'approval_type_id': self.approve_type_both.id})
        self.approve_request_employee_2.write({'approval_type_id': self.approve_type_both.id})
        # 1: Direct subordinates
        self.assertTrue(self.approve_request_employee.with_user(self.user_manager).can_approve)
        # 2: Indirect subordinates
        self.assertTrue(self.approve_request_employee_2.with_user(self.user_manager).can_approve)
    
    """
        Case: Employees have officer rights
    """
    def test_09_employee_rights_with_request(self):
    # Employee is a human resources manager who has the authority to approve all requests (Type: Approval Officer or Manager and Approval Officer)
        self.approve_request_employee.write({'approval_type_id': self.approve_type_hr.id})
        self.approve_request_employee_2.write({'approval_type_id': self.approve_type_both.id})
        self.assertTrue(self.approve_request_employee.with_user(self.user_approve_officer).can_approve)
        self.assertTrue(self.approve_request_employee_2.with_user(self.user_approve_officer).can_approve)
    
    """
        Case: Check approval action rights
    """
    def test_10_check_approval_action_rights(self):
    #Type: No validation
        # Employee
        self.assertTrue(self.approve_request_employee.with_user(self.user_employee_1).can_confirm)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_approve)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_validate)
        self.assertTrue(self.approve_request_employee.with_user(self.user_employee_1).can_done)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_refuse)
        # # Employee is manager
        self.approve_request_employee.invalidate_cache()
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_confirm)
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_approve)
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_validate)
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_done)
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_refuse)
        # Employee is a human resources manager
        self.approve_request_employee.invalidate_cache()
        self.assertFalse(self.approve_request_employee.with_user(self.user_approve_officer).can_confirm)
        self.assertFalse(self.approve_request_employee.with_user(self.user_approve_officer).can_approve)
        self.assertFalse(self.approve_request_employee.with_user(self.user_approve_officer).can_validate)
        self.assertFalse(self.approve_request_employee.with_user(self.user_approve_officer).can_done)
        self.assertFalse(self.approve_request_employee.with_user(self.user_approve_officer).can_refuse)
    
    def test_11_check_approval_action_rights(self):
    #Type: Manager
        self.approve_request_employee.write({'approval_type_id': self.approve_type_leader.id})
        # Employee
        self.assertTrue(self.approve_request_employee.with_user(self.user_employee_1).can_confirm)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_approve)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_validate)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_done)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_refuse)
        # # Employee is manager
        self.approve_request_employee.invalidate_cache()
        self.assertTrue(self.approve_request_employee.with_user(self.user_manager).can_confirm)
        self.assertTrue(self.approve_request_employee.with_user(self.user_manager).can_approve)
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_validate)
        self.assertTrue(self.approve_request_employee.with_user(self.user_manager).can_done)
        self.assertTrue(self.approve_request_employee.with_user(self.user_manager).can_refuse)
        # Employee is a human resources manager
        self.approve_request_employee.invalidate_cache()
        self.assertFalse(self.approve_request_employee.with_user(self.user_approve_officer).can_confirm)
        self.assertFalse(self.approve_request_employee.with_user(self.user_approve_officer).can_approve)
        self.assertFalse(self.approve_request_employee.with_user(self.user_approve_officer).can_validate)
        self.assertFalse(self.approve_request_employee.with_user(self.user_approve_officer).can_done)
        self.assertFalse(self.approve_request_employee.with_user(self.user_approve_officer).can_refuse)
    
    def test_12_check_approval_action_rights(self):
    #Type: Approval Officer
        self.approve_request_employee.write({'approval_type_id': self.approve_type_hr.id})
        # Employee
        self.assertTrue(self.approve_request_employee.with_user(self.user_employee_1).can_confirm)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_approve)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_validate)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_done)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_refuse)
        # # Employee is manager
        self.approve_request_employee.invalidate_cache()
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_confirm)
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_approve)
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_validate)
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_done)
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_refuse)
        # Employee is a human resources manager
        self.approve_request_employee.invalidate_cache()
        self.assertTrue(self.approve_request_employee.with_user(self.user_approve_officer).can_confirm)
        self.assertTrue(self.approve_request_employee.with_user(self.user_approve_officer).can_approve)
        self.assertFalse(self.approve_request_employee.with_user(self.user_approve_officer).can_validate)
        self.assertTrue(self.approve_request_employee.with_user(self.user_approve_officer).can_done)
        self.assertTrue(self.approve_request_employee.with_user(self.user_approve_officer).can_refuse)
        
    def test_13_check_approval_action_rights(self):
    #Type: Manager & Approval Officer
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_both.id, 
            'state': 'confirm'
        })
        # Employee
        self.assertTrue(self.approve_request_employee.with_user(self.user_employee_1).can_confirm)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_approve)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_validate)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_done)
        self.assertFalse(self.approve_request_employee.with_user(self.user_employee_1).can_refuse)
        # Employee is manager
        self.approve_request_employee.invalidate_cache()
        self.assertTrue(self.approve_request_employee.with_user(self.user_manager).can_confirm)
        self.assertTrue(self.approve_request_employee.with_user(self.user_manager).can_approve)
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_validate)
        self.assertFalse(self.approve_request_employee.with_user(self.user_manager).can_done)
        self.assertTrue(self.approve_request_employee.with_user(self.user_manager).can_refuse)
        # Employee is a human resources manager
        self.approve_request_employee.invalidate_cache()
        self.assertTrue(self.approve_request_employee.with_user(self.user_approve_officer).can_confirm)
        self.assertTrue(self.approve_request_employee.with_user(self.user_approve_officer).can_approve)
        self.assertTrue(self.approve_request_employee.with_user(self.user_approve_officer).can_validate)
        self.assertTrue(self.approve_request_employee.with_user(self.user_approve_officer).can_done)
        self.assertTrue(self.approve_request_employee.with_user(self.user_approve_officer).can_refuse)
