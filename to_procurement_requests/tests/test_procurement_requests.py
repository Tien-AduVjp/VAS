from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged

from .test_common import TestCommon

@tagged('post_install', '-at_install')
class TestProcurementRequests(TestCommon):

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
        request = self.env['replenishment.request'].create({
            'warehouse_id': self.ref('stock.warehouse0'),
            'scheduled_date': '2020-01-01',
            'responsible_id': self.user_request_manager_1.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
                'route_ids': [(4, self.product_route_1.id, 0)]
            })]
        })
        request.action_confirm()
        request.action_approve()

        # Check if stock picking is create
        self.assertTrue(request.picking_ids, "Picking is not created")

        # Check total move
        picking = request.picking_ids[0]
        self.assertEqual(len(picking.move_lines), 1, "Wrong number of stock move")

        # Check route on move
        move = picking.move_lines[0]
        self.assertEqual(move.rule_id.id, self.product_rule_1.id, "Wrong rule on stock move")

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

        # Setup product with route
        self.product.write({
            'route_ids': [(4, self.product_route_1.id)],
        })

        # Create request
        proc_request = self.env['replenishment.request'].create({
            'warehouse_id': self.ref('stock.warehouse0'),
            'scheduled_date': '2020-01-01',
            'responsible_id': self.user_request_manager_1.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
                'quantity': 0,
            })]
        })

        # Check if exception is raise
        self.assertRaises(ValidationError, proc_request.action_confirm)

    # FC003
    def test_create_empty_request(self):
        """
        Create empty request

        Input
        -----
        - Create replenishment request without any line
        - Confirm request

        Output
        ------
        - Get exception when confirming request

        """

        # Create request
        proc_request = self.env['replenishment.request'].create({
            'warehouse_id': self.ref('stock.warehouse0'),
            'scheduled_date': '2020-01-01',
            'responsible_id': self.user_request_manager_1.id,
        })

        # Check if exception is raise
        self.assertRaises(ValidationError, proc_request.action_confirm)

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
        request = self.env['replenishment.request'].create({
            'warehouse_id': self.ref('stock.warehouse0'),
            'scheduled_date': '2020-01-01',
            'responsible_id': self.user_request_manager_1.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
                'route_ids': [(4, self.product_route_1.id, 0)]
            })]
        })
        request.action_confirm()
        request.action_approve()

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
        request = self.env['replenishment.request'].create({
            'warehouse_id': self.ref('stock.warehouse0'),
            'scheduled_date': '2020-01-01',
            'responsible_id': self.user_request_manager_1.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
            })]
        })
        request.action_confirm()
        request.action_approve()

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
        request = self.env['replenishment.request'].create({
            'warehouse_id': self.ref('stock.warehouse0'),
            'scheduled_date': '2020-01-01',
            'responsible_id': self.user_request_manager_1.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
            })]
        })

        request2 = self.env['replenishment.request'].create({
            'warehouse_id': self.ref('stock.warehouse0'),
            'scheduled_date': '2020-07-01',
            'responsible_id': self.user_request_manager_1.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
                'quantity': 10,
            })]
        })

        # Not allowed to change warehouse and schedule date on waiting state
        request.action_confirm()
        with Form(request) as f:
            self.assertTrue(f._get_modifier('warehouse_id', 'readonly'))
            self.assertTrue(f._get_modifier('scheduled_date', 'readonly'))

        # Not allowed to change warehouse, schedule date and lines on waiting state on other states

        # Approve state
        request.action_approve()
        with Form(request) as f:
            self.assertTrue(f._get_modifier('warehouse_id', 'readonly'))
            self.assertTrue(f._get_modifier('scheduled_date', 'readonly'))
            self.assertTrue(f._get_modifier('line_ids', 'readonly'))

        # Done state
        request.action_done()
        with Form(request) as f:
            self.assertTrue(f._get_modifier('warehouse_id', 'readonly'))
            self.assertTrue(f._get_modifier('scheduled_date', 'readonly'))
            self.assertTrue(f._get_modifier('line_ids', 'readonly'))

        request2.action_confirm()
        # Refuse state
        request2.action_refuse()
        with Form(request2) as f:
            self.assertTrue(f._get_modifier('warehouse_id', 'readonly'))
            self.assertTrue(f._get_modifier('scheduled_date', 'readonly'))
            self.assertTrue(f._get_modifier('line_ids', 'readonly'))

        # Cancel state
        request2.action_cancel()
        with Form(request2) as f:
            self.assertTrue(f._get_modifier('warehouse_id', 'readonly'))
            self.assertTrue(f._get_modifier('scheduled_date', 'readonly'))
            self.assertTrue(f._get_modifier('line_ids', 'readonly'))

    # FC008
    def test_remove_request(self):
        """
        Test remove request

        Input
        -----
        - Create request
        - Check if request can be remove at each of its states

        Output
        ------
        - Only allowed to remove request on draft state

        """

        # Setup product with route
        self.product.write({
            'route_ids': [(4, self.product_route_1.id)],
        })

        # Create request
        request = self.env['replenishment.request'].create({
            'warehouse_id': self.ref('stock.warehouse0'),
            'scheduled_date': '2020-01-01',
            'responsible_id': self.user_request_manager_1.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
            })]
        })

        request2 = self.env['replenishment.request'].create({
            'warehouse_id': self.ref('stock.warehouse0'),
            'scheduled_date': '2020-01-01',
            'responsible_id': self.user_request_manager_1.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
            })]
        })

        # Only allowed to remove request on draft state
        request.action_confirm()
        self.assertRaises(ValidationError, request.unlink)
        request.action_approve()
        self.assertRaises(ValidationError, request.unlink)
        request.action_done()
        self.assertRaises(ValidationError, request.unlink)

        request2.action_confirm()
        request2.action_refuse()
        self.assertRaises(ValidationError, request2.unlink)
        request2.action_draft()
        request2.unlink()

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
        proc_request = self.env['replenishment.request'].create({
            'warehouse_id': self.ref('stock.warehouse0'),
            'scheduled_date': '2020-01-01',
            'responsible_id': self.user_request_manager_1.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
            })]
        })
        proc_request.action_confirm()
        self.assertRaises(UserError, proc_request.action_approve)

    # FC010
    def test_approve_request_send_email(self):
        """
        Test send email to responsible user when confirm request

        Input
        -----
        - Create replenishment request
        - Confirm request

        Output
        ------
        - Email will be send to reponsible user if they didn't confirm that request

        """

        # set auto_delete = False on email template so odoo won't delete after send
        self.env.ref('to_procurement_requests.email_template_submit_notification').write({
            'auto_delete': False
        })

        # Setup product with route
        self.product.write({
            'route_ids': [(4, self.product_route_1.id)],
        })

        # Create request
        request = self.env['replenishment.request'].create({
            'warehouse_id': self.ref('stock.warehouse0'),
            'scheduled_date': '2020-01-01',
            'responsible_id': self.user_request_manager_1.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
            })]
        })
        request.action_confirm()

        # Check if email record is exist
        mails = self.env['mail.mail'].search([
            ('model', '=', 'replenishment.request'),
            ('recipient_ids', 'in', self.user_request_manager_1.partner_id.ids)
        ])
        self.assertGreater(len(mails), 0)

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

        f = Form(self.env['replenishment.request'])
        f.warehouse_id = self.env.ref('stock.warehouse0')
        f.scheduled_date = '2020-01-01'
        f.responsible_id = self.user_request_manager_1
        request = f.save()

        # Test onchange UoM when creating new line
        with Form(request) as fe:
            with fe.line_ids.new() as line:
                line.product_id = self.product
        line = request.line_ids.search([('product_id', '=', self.product.id)], limit=1)
        self.assertEqual(line.uom_id.id, self.env.ref('uom.product_uom_unit').id, "UoM is not matched")

        # Test onchange UoM when edit line
        with Form(request) as fe:
            with fe.line_ids.edit(0) as line:
                line.product_id = self.product_2
        self.assertEqual(line.uom_id.id, self.env.ref('uom.product_uom_dozen').id, "UoM is not matched")

