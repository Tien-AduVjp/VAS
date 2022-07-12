odoo.define('to_pos_frontend_return.ReturnButton', function (require) {
    'use strict';

    const { useListener } = require('web.custom_hooks');
    const { useContext } = owl.hooks;
    const PosComponent = require('point_of_sale.PosComponent');
    const OrderManagementScreen = require('point_of_sale.OrderManagementScreen');
    const Registries = require('point_of_sale.Registries');
    const contexts = require('point_of_sale.PosContext');

    class ReturnButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this._onClick);
            this.orderManagementContext = useContext(contexts.orderManagement);
        }
        get canReturn() {
            const order = this.orderManagementContext.selectedOrder;
            if (!order || !order.locked || order.isFromClosedSession) {
                return false;
            } else {
                return true;
            }
        }
        async _onClick() {
            const order = this.orderManagementContext.selectedOrder;
            if (order) {
                var date_order = new Date(order.validation_date).getTime();
                var now = new Date().getTime();
                var expiry_date = new Date(date_order + this.env.pos.config.nod_return_product * 1000 * 60 * 60 * 24)
                var period = (now - date_order) / (1000 * 60 * 60 * 24);
                if (period > this.env.pos.config.nod_return_product && this.env.pos.config.nod_return_product) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Return order Error'),
                        body: _.str.sprintf(this.env._t('This order has exceeded the maximum number of days for return. Its return should have been done before %s'), expiry_date)
                    })
                } else {
                    this.showScreen('ReturnOrderScreen', { order: order });
                }
            }
        }
    }
    ReturnButton.template = 'ReturnButton';

    OrderManagementScreen.addControlButton({
        component: ReturnButton,
        condition: function () {
            return true;
        },
    });

    Registries.Component.add(ReturnButton);

    return ReturnButton;
});
