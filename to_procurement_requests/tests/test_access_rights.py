from datetime import datetime

from odoo.tests import tagged
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from .test_common import TestCommon

@tagged('post_install', '-at_install')
class TestAccessRights(TestCommon):

    def setUp(self):
        super(TestAccessRights, self).setUp()

        # Set default route on product
        self.product.write({
            'route_ids': [(4, self.product_route_1.id)],
        })

    # ST001
    def test_request_user_access(self):
        """
        Test request user group access rights. User can:
        - Allow to read, create and write but not remove request
        - Allow to read, create, write and remove request line
        - Allow to read stock move and stock picking
        - Not allow to approve request
        """

        # Request User can create request
        request = self.env['replenishment.request'].with_user(self.user_request_user_1).create({
            'warehouse_id': self.ref('stock.warehouse0'),
            'scheduled_date': '2020-01-01',
            'responsible_id': self.user_request_manager_1.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'uom_id': self.product.uom_id.id,
                'quantity': 5,
            })]
        })

        # Request User can edit request
        request.with_user(self.user_request_user_1).write({'scheduled_date': '2020-02-01'})
        self.assertEqual(request.scheduled_date, datetime.strptime('2020-02-01', DEFAULT_SERVER_DATE_FORMAT).date())

        # Request User can read/write other's requests
        request.with_user(self.user_request_user_2).read(['warehouse_id'])
        request.with_user(self.user_request_user_2).write({'scheduled_date': '2020-03-01'})

        # but can't remove request
        self.assertRaises(ValidationError, request.with_user(self.user_request_user_2).unlink)

        # Request User can confirm request but approve
        request.with_user(self.user_request_user_1).action_confirm()
        self.assertRaises(ValidationError, request.with_user(self.user_request_user_1).action_approve)

        # Only Request Manager can approve request
        request.with_user(self.user_request_manager_1).action_approve()

        # User allowed to read stock picking and stock move created from request
        picking = request.picking_ids[0]
        picking.with_user(self.user_request_user_1).read(['name'])
        move_line = picking.move_lines[0]
        move_line.with_user(self.user_request_user_1).read(['name'])

    # ST002
    def test_stock_user_access(self):
        """
        Check stock user access. Stock user can
        - Read and modify request but can't create or delete
        """

        self.user_stock_user = self.env['res.users'].create({
            'name': 'Leo Stock User',
            'login': 'leo_stock_user',
            'email': 'leo.stock.user@example.viindoo.com',
            'groups_id': [(6, 0, [self.ref('base.group_user'), self.ref('stock.group_stock_user')])]
        })

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

        # Stock user can read or change request
        request.with_user(self.user_stock_user).read(['name'])
        request.with_user(self.user_stock_user).write({'scheduled_date': '2021-01-01'})
