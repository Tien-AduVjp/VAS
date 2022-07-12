odoo.define('to_loyalty_pos.LoyaltyPoints', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class LoyaltyPoints extends PosComponent { }
    LoyaltyPoints.template = 'LoyaltyPoints';

    Registries.Component.add(LoyaltyPoints);

    return LoyaltyPoints;
});
