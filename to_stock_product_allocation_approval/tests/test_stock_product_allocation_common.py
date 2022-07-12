from odoo.addons.stock.tests.common2 import TestStockCommon
from odoo.addons.to_approvals.tests.common import Common


class TestStockProductAllocationCommon(TestStockCommon,Common):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        cls.stock_location_approval_type = cls.env['approval.request.type'].search([('name', '=', 'Stock Allocation Approval')], limit=1)

        # Create warehouse
        cls.warehouse_2 = cls.env['stock.warehouse'].create({
            'name': 'Warehouse 2',
            'reception_steps': 'one_step',
            'delivery_steps': 'ship_only',
            'code': 'WH2'})

        cls.warehouse_3 = cls.env['stock.warehouse'].create({
            'name': 'Warehouse 3',
            'reception_steps': 'one_step',
            'delivery_steps': 'ship_only',
            'code': 'WH3'})

        # Prepare the dict of values to stock allocaton request line
        val_1 = {
            'product_id': cls.product_2.id,
            'quantity': 10,
            'warehouse_id': cls.warehouse_2.id,
            'uom_id': cls.product_2.uom_id.id
            }

        val_2 = {
            'product_id': cls.product_3.id,
            'quantity': 5,
            'warehouse_id': cls.warehouse_3.id,
            'uom_id': cls.product_3.uom_id.id
            }

        # Create stock allocation request
        cls.allocation_request_1 = cls.env['approval.request'].create({
            'warehouse_id': cls.warehouse_1.id,
            'allocation_request_line_ids': [(0, 0, val_1), (0, 0, val_2)],
            'approval_type_id': cls.stock_location_approval_type.id,
            'employee_id': cls.env.ref('hr.employee_al').id,
            'currency_id': cls.env.company.currency_id.id,
            })

        # Create stock allocation request with stock user
        val_3 = {
            'product_id': cls.product_4.id,
            'quantity': 10,
            'warehouse_id': cls.warehouse_2.id,
            'uom_id': cls.product_4.uom_id.id
            }
        val_4 = {
            'product_id': cls.product_5.id,
            'quantity': 15,
            'warehouse_id': cls.warehouse_3.id,
            'uom_id': cls.product_5.uom_id.id
            }

        cls.allocation_request_2 = cls.env['approval.request'].create({
            'warehouse_id': cls.warehouse_1.id,
            'allocation_request_line_ids': [(0, 0, val_3), (0, 0, val_4)],
            'approval_type_id': cls.stock_location_approval_type.id,
            'employee_id': cls.env.ref('hr.employee_al').id,
            'currency_id': cls.env.company.currency_id.id,
            })
