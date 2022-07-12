odoo.define('to_loyalty_pos.OrderWidget', function (require) {
    'use strict';

    const OrderWidget = require('point_of_sale.OrderWidget');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    const LoyaltyOrderWidget = (OrderWidget) =>
        class extends OrderWidget {
            constructor() {
                super(...arguments);
                this.state.points_won = 0;
                this.state.points_spent = 0;
                this.state.points_total = 0;
            }
            get isNegative() {
                return this.state.points_total < 0;
            }
            get showLoyaltyPoint() {
                if (this.env.pos.loyalty && this.env.pos.get_order().get_client()) {
                    return true;
                } else {
                    return false;
                }
            }
            get loyaltyRounding() {
                return this.env.pos.loyalty.rounding;
            }
            get points_won() {
                return round_pr(this.state.points_won, this.loyaltyRounding);
            }
            get points_spent() {
                return round_pr(this.state.points_spent, this.loyaltyRounding);
            }
            get points_total() {
                return round_pr(this.state.points_total, this.loyaltyRounding);
            }
            _updateSummary() {
                var order = this.env.pos.get_order();
                if (this.env.pos.loyalty && order.get_client()) {
                    this.state.points_won = order.get_won_points();
                    this.state.points_spent = order.get_spent_points();
                    this.state.points_total = order.get_new_total_points();
                }
                super._updateSummary()
            }
        };

    Registries.Component.extend(OrderWidget, LoyaltyOrderWidget);

    return OrderWidget;
});
