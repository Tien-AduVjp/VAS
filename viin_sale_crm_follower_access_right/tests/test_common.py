from odoo.tests.common import TransactionCase


class TestCommon(TransactionCase):

    def setUp(self):
        super(TestCommon, self).setUp()
        self.user1 = self.env['res.users'].create({
            'name': 'user test',
            'login': 'user test',
            'groups_id': [(6, 0, [self.env.ref('sales_team.group_sale_salesman').id])]
        })
        self.sale_order1 = self.env['sale.order'].create({
            'partner_id': self.env['res.partner'].create({'name': 'partner test'}).id
        })
        self.sale_order_line1 = self.env['sale.order.line'].create({
            'product_id': self.env.ref('product.product_product_1').id,
            'order_id': self.sale_order1.id
        })
        self.crm_lead1 = self.env['crm.lead'].create({
            'name': 'Test'
        })
