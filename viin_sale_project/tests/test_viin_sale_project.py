from odoo.exceptions import AccessError
from odoo.tests.common import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestViinSaleProject(SavepointCase):

    def setUp(self):
        super(TestViinSaleProject, self).setUp()

        self.env = self.env(context=dict({'tracking_disable': True}, **self.env.context))
        self.user1 = self.env.ref('base.user_demo')
        self.user1.groups_id = [(6, 0, [self.env.ref('project.group_project_user').id])]

        self.product_test = self.env['product.product'].create({
            'name': 'Product Service Test',
            'type': 'service',
            'invoice_policy': 'delivery',
            'service_type': 'timesheet'
        })
        self.project1 = self.env['project.project'].create({
            'name': 'project test',
            'allow_billable': True,
            'allow_timesheets': True,
            'bill_type': 'customer_project',
            'partner_id': self.env.ref('base.res_partner_1').id
        })

    def test_record_rule(self):
        # case 1:
        wizard = self.env['project.create.sale.order']\
            .with_context(active_model='project.project', active_id=self.project1.id)\
            .create({
                'partner_id': self.env.ref('base.res_partner_1').id,
                'line_ids': [
                    (0, 0, {
                        'product_id': self.product_test.id,
                        'price_unit': 15
                    })
                ]
            })
        action = wizard.action_create_sale_order()
        sale_order = self.env['sale.order'].browse(action['res_id'])

        with self.assertRaises(AccessError):
            sale_order.order_line.with_user(self.user1).read(['id'])
        with self.assertRaises(AccessError):
            sale_order.with_user(self.user1).read(['id'])

        self.project1.user_id = self.user1.id

        sale_order.order_line.with_user(self.user1).read(['id'])
        sale_order.with_user(self.user1).read(['id'])
