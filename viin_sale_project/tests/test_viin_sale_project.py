from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestViinSaleProject(TransactionCase):

    def setUp(self):
        super(TestViinSaleProject, self).setUp()
        self.user1 = self.env['res.users'].create({
            'name': 'Project user',
            'login': 'project user',
            'groups_id': [(6, 0, [self.env.ref('project.group_project_user').id])]
        })
        self.product_test = self.env['product.product'].create({
            'name': 'Product Service Test',
            'type': 'service',
            'invoice_policy': 'delivery',
            'service_type': 'timesheet'
        })
        self.project1 = self.env['project.project'].create({
            'name': 'project test'
        })

    def test_record_rule(self):
        # case 1:
        wizard = self.env['project.create.sale.order'].with_context(active_model='project.project', active_id=self.project1.id).create({
            'product_id': self.product_test.id,
            'price_unit': 1.0,
            'billable_type': 'project_rate',
            'partner_id': self.user1.partner_id.id,
        })
        action = wizard.action_create_sale_order()
        sale_order = self.env['sale.order'].browse(action['res_id'])

        with self.assertRaises(AccessError):
            sale_order.order_line.with_user(self.user1).read(['name'])
        with self.assertRaises(AccessError):
            sale_order.with_user(self.user1).read()

        self.project1.user_id = self.user1.id

        sale_order.order_line.with_user(self.user1).read(['name'])
        sale_order.with_user(self.user1).read(['name'])
