from odoo.exceptions import UserError
from odoo.tests import Form, tagged
from odoo import fields

from .test_common import TestCommon


@tagged('post_install', 'at_install')
class TestProcurementRequests(TestCommon):

    def test_generate_approval_type(self):
        self.assertTrue(self.approval_procurement_type)

    # FC002
    def test_create_zero_quantity_request(self):
        """
        Create zero quantity replenishment request for product with configured route

        Input
        -----
        - Set product to use route to pull product from input to stock
        - Create replenishment request for product and set quantity to 0
        - Confirm request

        Output
        ------
        - Get exception when confirming request

        """
        # Create request
        request = self.env['approval.request'].create({
            'title': 'Procurement Approval Request 1',
            'employee_id': self.ref('hr.employee_al'),
            'approval_type_id': self.approval_procurement_type.id,
            'currency_id': self.env.company.currency_id.id,
            'deadline': fields.Date.today(),
            'procurement_request_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'warehouse_id': self.ref('stock.warehouse0'),
                'uom_id': self.product.uom_id.id,
                'quantity': 0,
                'route_ids': [(4, self.product_route_1.id, 0)],
            })]
        }).with_user(self.ref('base.user_admin'))

        # Check if exception is raise
        self.assertRaises(UserError, request.action_confirm)

    # FC001+FC005
    def test_create_request_with_product_configured(self):
        """
        Test create request with route for configured product

        Input
        -----
        - Use product with multiple routes configured
        - Create replenishment request with one route
        - Confirm and approve request

        Output
        ------
        - Stock picking is created for choosen route

        """

        # Setup product with route
        self.product.write({
            'route_ids': [(6, 0, [self.product_route_1.id, self.product_route_2.id])],
        })

        # Create request
        request = self.env['approval.request'].create({
            'title': 'Procurement Approval Request 1',
            'employee_id': self.ref('hr.employee_al'),
            'approval_type_id': self.approval_procurement_type.id,
            'currency_id': self.env.company.currency_id.id,
            'deadline': fields.Date.today(),
            'procurement_request_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'warehouse_id': self.ref('stock.warehouse0'),
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
                'route_ids': [(4, self.product_route_1.id, 0)],
            })]
        }).with_user(self.ref('base.user_admin'))
        request.action_confirm()
        request.action_validate()

        # Check if stock picking is create
        self.assertTrue(request.picking_ids, "Picking is not created")

        # Check total move
        picking = request.picking_ids[0]
        self.assertEqual(len(picking.move_lines), 1, "Wrong number of stock move")

        # Check route on move
        move = picking.move_lines[0]
        self.assertEqual(move.rule_id.id, self.product_rule_1.id, "Wrong rule on stock move")

    # FC004
    def test_create_request_with_other_route(self):
        """
        Test create request without route

        Input
        -----
        - Use product without routes configured
        - Create replenishment request with route
        - Confirm request

        Output
        ------
        - Stock picking is created if route is valid

        """

        # Create request
        request = self.env['approval.request'].create({
            'title': 'Procurement Approval Request',
            'employee_id': self.ref('hr.employee_al'),
            'approval_type_id': self.approval_procurement_type.id,
            'currency_id': self.env.company.currency_id.id,
            'deadline': fields.Date.today(),
            'procurement_request_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'warehouse_id': self.ref('stock.warehouse0'),
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
                'route_ids': [(4, self.product_route_1.id, 0)],
            })]
        }).with_user(self.ref('base.user_admin'))
        request.action_confirm()
        request.action_validate()

        # Check if stock picking is create
        self.assertTrue(request.picking_ids, "Picking is not created")

        # Check total move
        picking = request.picking_ids[0]
        self.assertEqual(len(picking.move_lines), 1, "Wrong number of stock move")

        # Check route on move
        move = picking.move_lines[0]
        self.assertEqual(move.rule_id.id, self.product_rule_1.id, "Wrong rule on stock move")

    # FC006
    def test_create_default_request(self):
        """
        Create replenishment request without choosing route for product with configured route

        Input
        -----
        - Set product to use route to pull product from input to stock
        - Create replenishment request for that product without choosing route
        - Approve request

        Output
        ------
        - Route set on product is triggered
        - Stock picking is created from request

        """

        # Setup product with route
        self.product.write({
            'route_ids': [(4, self.product_route_1.id)],
        })

        # Create request and run
        request = self.env['approval.request'].create({
            'title': 'Procurement Approval Request',
            'employee_id': self.ref('hr.employee_al'),
            'approval_type_id': self.approval_procurement_type.id,
            'currency_id': self.env.company.currency_id.id,
            'deadline': fields.Date.today(),
            'procurement_request_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'warehouse_id': self.ref('stock.warehouse0'),
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
                'route_ids': [(4, self.product_route_1.id, 0)],
            })]
        }).with_user(self.ref('base.user_admin'))
        request.action_confirm()
        request.action_validate()

        # Check if stock picking is create
        self.assertTrue(request.picking_ids, "Picking is not created")

        # Check total move
        picking = request.picking_ids[0]
        self.assertEqual(len(picking.move_lines), 1, "Wrong number of stock move")

        # Check route on move
        move = picking.move_lines[0]
        self.assertEqual(move.rule_id.id, self.product_rule_1.id, "Wrong rule on stock move")

    # FC007
    def test_edit_request(self):
        """
        Test edit request

        Input
        -----
        - Create request
        - Check if request can be edit at each of its states

        Output
        ------
        - Only allowed to edit warehouse and schedule date on draft state
        - Only allowed to edit lines on draft and waiting state

        """

        # Setup product with route
        self.product.write({
            'route_ids': [(4, self.product_route_1.id)],
        })

        # Create request
        request = self.env['approval.request'].create({
            'title': 'Procurement Approval Request',
            'employee_id': self.ref('hr.employee_al'),
            'approval_type_id': self.approval_procurement_type.id,
            'currency_id': self.env.company.currency_id.id,
            'deadline': fields.Date.today(),
            'procurement_request_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'warehouse_id': self.ref('stock.warehouse0'),
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
            })]
        }).with_user(self.ref('base.user_admin'))

        request2 = self.env['approval.request'].create({
            'title': 'Procurement Approval Request',
            'employee_id': self.ref('hr.employee_al'),
            'approval_type_id': self.approval_procurement_type.id,
            'currency_id': self.env.company.currency_id.id,
            'deadline': fields.Date.today(),
            'procurement_request_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'warehouse_id': self.ref('stock.warehouse0'),
                'uom_id': self.product.uom_id.id,
                'quantity': 10,
            })]
        }).with_user(self.ref('base.user_admin'))

        # Not allowed to change warehouse and schedule date on waiting state
        request.action_confirm()
        with Form(request) as f:
            self.assertTrue(f._get_modifier('procurement_request_line_ids', 'readonly'))

        # Not allowed to change warehouse, schedule date and lines on waiting state on other states

        # Approve state
        request.action_validate()
        with Form(request) as f:
            self.assertTrue(f._get_modifier('procurement_request_line_ids', 'readonly'))


        # Done state
        request.action_done()
        with Form(request) as f:
            self.assertTrue(f._get_modifier('procurement_request_line_ids', 'readonly'))


        request2.action_confirm()
        # Refuse state
        request2.action_refuse()
        with Form(request2) as f:
            self.assertTrue(f._get_modifier('procurement_request_line_ids', 'readonly'))


        # Cancel state
        request2.action_cancel()
        with Form(request2) as f:
            self.assertTrue(f._get_modifier('procurement_request_line_ids', 'readonly'))

    # FC009
    def test_create_request_without_route(self):
        """
        Test creat request without route

        Input
        -----
        - Use product without routes configured
        - Create replenishment request without choosing route for product
        - Confirm request
        - Approve request

        Output
        ------
        - Get exception when approve request

        """

        # Create request
        proc_request = self.env['approval.request'].create({
            'title': 'Procurement Approval Request',
            'employee_id': self.ref('hr.employee_al'),
            'approval_type_id': self.approval_procurement_type.id,
            'currency_id': self.env.company.currency_id.id,
            'deadline': fields.Date.today(),
            'procurement_request_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'warehouse_id': self.ref('stock.warehouse0'),
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
            })]
        })
        proc_request.action_confirm()
        self.assertRaises(UserError, proc_request.action_validate())

    # FT001
    def test_onchange_product(self):
        """
        Test onchange product on request line

        Input
        -----
        - Change product on request line

        Output
        ------
        - UoM is changed

        """
        self.product_2 = self.env['product.product'].create({
            'name': 'Doggo',
            'type': 'product',
            'uom_id': self.env.ref('uom.product_uom_dozen').id,
            'categ_id': self.env.ref('product.product_category_all').id
        })

        f = Form(self.env['approval.request'])
        f.approval_type_id = self.approval_procurement_type
        f.employee_id = self.env.ref('hr.employee_al')
        f.currency_id = self.env.company.currency_id
        with f.procurement_request_line_ids.new() as line:
            line.warehouse_id = self.env.ref('stock.warehouse0')
            line.product_id = self.product
            line.quantity = 5
        request = f.save()

        # Test onchange UoM when creating new line
        with Form(request) as fe:
            with fe.procurement_request_line_ids.new() as line:
                line.product_id = self.product
        line = request.procurement_request_line_ids.search([('product_id', '=', self.product.id)], limit=1)
        self.assertEqual(line.uom_id.id, self.env.ref('uom.product_uom_unit').id, "UoM is not matched")

        # Test onchange UoM when edit line
        with Form(request) as fe:
            with fe.procurement_request_line_ids.edit(0) as line:
                line.product_id = self.product_2
        self.assertEqual(line.uom_id.id, self.env.ref('uom.product_uom_dozen').id, "UoM is not matched")

    def test_generate_rfq_after_approve(self):
        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy')
        route_buy.rule_ids[:1].group_propagation_option = 'propagate'

        self.env['product.supplierinfo'].create({
                'name': self.ref('base.res_partner_1'),
                'product_tmpl_id': self.product.product_tmpl_id.id,
                'price': 1000,
            })

        request = self.env['approval.request'].create({
            'title': 'Procurement Approval Request',
            'employee_id': self.ref('hr.employee_al'),
            'approval_type_id': self.approval_procurement_type.id,
            'currency_id': self.env.company.currency_id.id,
            'deadline': fields.Date.today(),
            'procurement_request_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'warehouse_id': self.ref('stock.warehouse0'),
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
                'route_ids': [(6, 0, route_buy.ids)]
            })]
        }).with_user(self.ref('base.user_admin'))
        request.action_confirm()
        request.action_validate()

        self.assertTrue(request.purchase_order_ids)

    def test_generate_rfq_with_product_service(self):
        self.env['product.supplierinfo'].create({
            'name': self.ref('base.res_partner_1'),
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'price': 1000,
        })
        self.product.type = 'service'

        request = self.env['approval.request'].create({
            'title': 'Procurement Approval Request',
            'employee_id': self.ref('hr.employee_al'),
            'approval_type_id': self.approval_procurement_type.id,
            'currency_id': self.env.company.currency_id.id,
            'deadline': fields.Date.today(),
            'procurement_request_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'warehouse_id': self.ref('stock.warehouse0'),
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
            })]
        }).with_user(self.ref('base.user_admin'))
        request.action_confirm()
        request.action_validate()

        self.assertTrue(request.purchase_order_ids)
