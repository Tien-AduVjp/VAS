from odoo.tests import common


class Common(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner_a = cls.env.ref('base.res_partner_1')
        cls.partner_b = cls.env.ref('base.res_partner_2')

        cls.product_table_mto = cls.env.ref('mrp.product_product_computer_desk')
        cls.product_table_top = cls.env.ref('mrp.product_product_computer_desk_head')
        cls.product_table_leg = cls.env.ref('mrp.product_product_computer_desk_leg')
        cls.product_bolt = cls.env.ref('mrp.product_product_computer_desk_bolt')
        cls.product_screw = cls.env.ref('mrp.product_product_computer_desk_screw')
        cls.product_wood_panel = cls.env.ref('mrp.product_product_wood_panel')

    def _create_mps(self, product, target_qty=30, min_replenish_qty=10, max_replenish_qty=100):
        return self.env['mrp.production.schedule'].create({
            'product_id': product.id,
            'forecast_target_qty': target_qty,
            'min_to_replenish_qty': min_replenish_qty,
            'max_to_replenish_qty': max_replenish_qty,
            })
