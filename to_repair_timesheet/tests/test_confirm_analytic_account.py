from odoo.tests import Form, tagged
from .common import TestRepairTimesheetCommon


@tagged('-at_install', 'post_install')
class TestROConfirmAnalyticAccount(TestRepairTimesheetCommon):
    def setUp(self):
        super().setUp()
        
    def test_01_no_analytic_account_created(self):
        """
            2 repair fee line with product
                'service_policy': 'delivered_timesheet',
                'service_tracking': 'task_global_project',
                'expense_policy': 'no',
            
            Input:
                Create 1 repair order and confirm it
            
            Expect:
                no analytic account created for the repair order
        """
        self.service_product.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'expense_policy': 'no',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
        self.service_product_2.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'expense_policy': 'no',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
        
        repair_order = self._create_repair_order([self.service_product, self.service_product_2])
        
        self.assertFalse(bool(repair_order.analytic_account_id))
        
    def test_02_created_analytic_account(self):
        """
            2 repair fee line with product
                'service_policy': 'delivered_timesheet',
                'service_tracking': 'project_only',
                'expense_policy': 'no',
            
            Input:
                Create 1 repair order and confirm it
            
            Expect:
                A analytic account created for the repair order
        """
        self.service_product.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'project_only',
            'expense_policy': 'no',
        })
        self.service_product_2.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'project_only',
            'expense_policy': 'no',
        })
        
        repair_order = self._create_repair_order([self.service_product, self.service_product_2])
        
        self.assertTrue(bool(repair_order.analytic_account_id))
        
    def test_03_created_analytic_account(self):
        """
            1 repair fee line with product
                'service_policy': 'delivered_timesheet',
                'service_tracking': 'task_global_project',
                'expense_policy': 'no',
            1 repair fee line with product
                'service_policy': 'delivered_timesheet',
                'service_tracking': 'projecttask_global_project_only',
                'expense_policy': 'cost',
            
            Input:
                Create 1 repair order and confirm it
            
            Expect:
                A analytic account created for the repair order
        """
        self.service_product.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'expense_policy': 'no',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
        self.service_product_2.write({
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_global_project',
            'expense_policy': 'cost',
            'project_id': self.env.ref('sale_timesheet.project_support').id,
        })
        
        repair_order = self._create_repair_order([self.service_product, self.service_product_2])
        
        self.assertTrue(bool(repair_order.analytic_account_id))
