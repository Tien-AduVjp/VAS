from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestPosOrder(HttpCase):

    def test_payment_by_promotion_voucher(self):
        env = self.env(user=self.env.ref('base.user_admin'))
        #Create product for POS
        env.ref('product.product_delivery_01').write({
            'name': 'product_1',
            'categ_id': env.ref('product.product_category_1').id,
            'price': 400.00,
            'standard_price': 400.00,
            'available_in_pos': True,
            'pos_categ_id': env.ref('point_of_sale.pos_category_desks').id
        })

        #create voucher type
        voucher_type = env.ref('to_promotion_voucher.voucher_type_generic').write({
            'value': 500.00
        })

        #Create product voucher
        product_voucher = env.ref('point_of_sale.desk_organizer')
        product_voucher.write({
            'tracking':'serial',
            'is_promotion_voucher': True,
            'voucher_type_id': env.ref('to_promotion_voucher.voucher_type_generic').id,
        })

        #Create picking type
        picking_type = env['stock.picking.type'].search([('code', '=', 'voucher_issue_order'), ('company_id', '=', env.company.id)], limit=1)
        picking_type.write({
            'default_location_dest_id':env.ref('stock.stock_location_stock').id
        })

        #Issue voucher
        voucher = env['voucher.issue.order'].create({
            'product_id': product_voucher.id,
            'voucher_qty': 10,
            'product_uom_id': product_voucher.uom_id.id,
            'picking_type_id': picking_type.id,
            'valid_duration': 30,
            'company_id': env.company.id
        })
        voucher.action_confirm()
        voucher.action_issue()

        #Give voucher
        voucher_give_order = env['voucher.give.order'].create({'origin': 'My Company'})
        voucher_give_order.write({'voucher_ids': [(6, 0, voucher.move_finished_ids.move_line_ids.voucher_id[0:4].mapped('id'))]  })
        voucher_give_order.action_confirm()
        voucher_give_order.action_give()

        #Voucher
        #actived
        voucher.move_finished_ids.move_line_ids.voucher_id[0].write({'serial':'voucher_actived'})
        #expired
        voucher.move_finished_ids.move_line_ids.voucher_id[1].write({'state': 'expired','serial':'voucher_expired'})
        #used
        voucher.move_finished_ids.move_line_ids.voucher_id[2].write({'state': 'used', 'value': 0, 'serial':'voucher_used'})
        #used 100
        voucher.move_finished_ids.move_line_ids.voucher_id[3].write({'state': 'used','serial':'voucher_used_100', 'used_amount': 100})
        #inactived
        voucher.move_finished_ids.move_line_ids.voucher_id[4].write({'serial':'voucher_inactived'})

        #Config for a point of sale
        cash_journal = env['account.journal'].search([('code', '=', 'PVJ'), ('company_id', '=', env.company.id)], limit=1)
        pos_config = env.ref('point_of_sale.pos_config_main')
        cash_method = pos_config.payment_method_ids.filtered(lambda r: r.is_cash_count)
        cash_method.write({
            'cash_journal_id': cash_journal.id
        })

        #Case 1
        self.payment_by_promotion_voucher(env, pos_config, 'promotion_voucher_pos_actived')
        #Case 2
        self.payment_by_promotion_voucher(env, pos_config, 'promotion_voucher_pos_expired')
        #Case 3
        self.payment_by_promotion_voucher(env, pos_config, 'promotion_voucher_pos_used')
        #Case 4
        self.payment_by_promotion_voucher(env, pos_config, 'promotion_voucher_pos_inactived')
        #Case 5
        self.payment_by_promotion_voucher(env, pos_config, 'promotion_voucher_pos_incorect')
        #Case 6
        self.payment_by_promotion_voucher(env, pos_config, 'promotion_voucher_pos_actived_used')

    def payment_by_promotion_voucher(self, env, pos_config, promotion_voucher_pos_product):
        pos_config.open_session_cb()
        self.start_tour("/pos/web?config_id=%d" % pos_config.id, promotion_voucher_pos_product, login="admin")
        pos_order = env['pos.order'].search([('session_id', '=', pos_config.current_session_id.id)])
        pos_config.current_session_id.action_pos_session_closing_control()
