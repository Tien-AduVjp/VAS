from datetime import datetime

from odoo.tests import common

from odoo.addons.to_account_asset.tests.asset_common import AssetCommon


@common.tagged('post_install', '-at_install')
class TestAssetPurchaseCommon(AssetCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.uom_unit = cls.env.ref('uom.product_uom_unit')

        cls.product_product = cls.env['product.product'].create({'type': 'product',
                                                                 'name': 'product_product',
                                                                 'asset_category_id': cls.asset_category.id,
                                                                 })
        cls.product_comsu = cls.env['product.product'].create({'type': 'consu', 'name': 'product_consu'})

    def _make_purchase_order(self, product, partner_a):
        return self.env['purchase.order'].create({
            'partner_id': partner_a.id,
            'order_line': [
                (0, 0, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom': self.uom_unit.id,
                    'product_qty': 1.0,
                    'price_unit': 100.0,
                    'date_planned': datetime.today(),
                }),
            ],
        })

    def _create_invoice_from_po(self, purchase_order):
        purchase_order.button_confirm()

        f = common.Form(self.env['account.move'].with_context(default_type='in_invoice'))
        f.partner_id = purchase_order.partner_id
        f.purchase_id = purchase_order
        invoice = f.save()
        invoice.post()
        purchase_order.flush()
        return invoice
