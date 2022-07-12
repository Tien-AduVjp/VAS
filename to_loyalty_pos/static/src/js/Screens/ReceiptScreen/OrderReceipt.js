odoo.define('to_loyalty_pos.OrderReceipt', function (require) {
    'use strict';

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    const LoyaltyOrderReceipt = (OrderReceipt) =>
        class extends OrderReceipt {
            get loyalty() {
                return this.env.pos.loyalty;
            }
            get points_won() {
                return round_pr(this.receiptEnv.order.get_won_points(), this.loyalty.rounding);
            }
            get points_spent() {
                return round_pr(this.receiptEnv.order.get_spent_points(), this.loyalty.rounding);
            }
            get points_total() {
                return round_pr(this.receiptEnv.order.get_new_total_points(), this.loyalty.rounding);
            }
        };

    Registries.Component.extend(OrderReceipt, LoyaltyOrderReceipt);

    return OrderReceipt;
});
