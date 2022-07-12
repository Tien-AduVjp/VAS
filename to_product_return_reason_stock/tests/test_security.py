from odoo.tests.common import tagged
from odoo.addons.to_product_return_reason.tests.common import ProductReturnReasonCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestSecurity(ProductReturnReasonCommon):

    def test_stock_group_stock_user(self):
        group_stock_user = self.env.ref('stock.group_stock_user').id
        self.user_1.write({'groups_id': [(6, 0, [group_stock_user])]})
        
        self.reason_1.with_user(self.user_1).read(['id'])
        self.reason_1.with_user(self.user_1).write({'name': 'name_test'})
        self.reason_1.with_user(self.user_1).unlink()
        self.env['product.return.reason'].with_user(self.env['product.return.reason']).create({
                'name': 'test_new',
                'description': 'description_new'
            })
