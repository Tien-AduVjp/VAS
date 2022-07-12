from odoo.exceptions import AccessError
from odoo.tests.common import SavepointCase


class ProductReturnReasonCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(ProductReturnReasonCommon, cls).setUpClass()
        cls.user_1 = cls.env.ref('base.user_demo')
        cls.user_2 = cls.env.ref('base.demo_user0')
        cls.reason_1 = cls.env['product.return.reason'].create({
            'name': 'reason_1',
            'description': 'description',
        })
