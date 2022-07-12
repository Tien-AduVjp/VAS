from odoo.tests.common import SavepointCase, Form


class TestCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        User = cls.env['res.users']
        group_voucher_user = cls.env.ref('to_promotion_voucher.group_promotion_voucher_user')
        group_voucher_manager = cls.env.ref('to_promotion_voucher.group_promotion_voucher_manager')
        group_stock_user = cls.env.ref('stock.group_stock_user')
        group_stock_manager = cls.env.ref('stock.group_stock_manager')
        cls.Warehouse = cls.env['stock.warehouse']
        cls.StockLocation = cls.env['stock.location']
        cls.ProductTemplate = cls.env['product.template']
        cls.Product = cls.env['product.product'].with_context(default_is_promotion_voucher=True)
        cls.VoucherType = cls.env['voucher.type']
        cls.VoucherIssueOrder = cls.env['voucher.issue.order']
        cls.VoucherMoveOrder = cls.env['voucher.move.order']
        cls.Voucher = cls.env['voucher.voucher']
        cls.product_category = cls.env.ref('to_promotion_voucher.product_category_promotion_voucher')
        cls.GiveVoucher = cls.env['voucher.give.order']
        cls.ExtendVoucher = cls.env['extend.expired.vouchers']
        cls.cron_hero = cls.env.ref('to_promotion_voucher.ir_cron_scheduler_check_expired_voucher')
        cls.voucher_type = cls.env.ref('to_promotion_voucher.voucher_type_generic')
        cls.promotion_voucher_user = User.create({
            'name': 'Voucher User',
            'login': 'voucher_user',
            'email': 'user@example.viindoo.com',
            'notification_type': 'email',
            'groups_id': [(6, 0, [group_voucher_user.id, group_stock_user.id])],
        })
        cls.promotion_voucher_manager = User.create({
            'name': 'Voucher Manager',
            'login': 'voucher_manager',
            'email': 'manager@example.viindoo.com',
            'notification_type': 'email',
            'groups_id': [(6, 0, [group_voucher_manager.id, group_stock_manager.id])],
        })
        cls.voucher_product_form = Form(cls.Product)
        cls.voucher_product_form.name = 'Voucher'
        cls.voucher_product_form.voucher_type_id = cls.voucher_type
        cls.voucher_product = cls.voucher_product_form.save()
        cls.voucher = cls.Voucher.create({'name': 'Voucher 10%'})
        cls.give_voucher = cls.GiveVoucher.create({'origin': 'My Company'})
        cls.stock_warehouse = cls.Warehouse.create({'name': 'Demo', 'code': 'DEMO'})
        cls.voucher_move_order_form = Form(cls.VoucherMoveOrder)
        cls.voucher_move_order_form.warehouse_id = cls.stock_warehouse
        cls.voucher_move_order = cls.voucher_move_order_form.save()
