odoo.define('to_product_return_reason_pos.ReturnOrderScreen', function (require) {
    'use strict';

    const ReturnOrderScreen = require('to_pos_frontend_return.ReturnOrderScreen');
    const Registries = require('point_of_sale.Registries');

    const ReasonReturnOrderScreen = (ReturnOrderScreen) =>
        class extends ReturnOrderScreen {
            get return_reasons() {
                return this.env.pos.return_reasons;
            }
        }
    Registries.Component.extend(ReturnOrderScreen, ReasonReturnOrderScreen);
    return ReturnOrderScreen;
});
