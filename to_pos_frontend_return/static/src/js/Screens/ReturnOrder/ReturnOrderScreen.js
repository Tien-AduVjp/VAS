odoo.define('to_pos_frontend_return.ReturnOrderScreen', function (require) {
    'use strict';

    const { useState } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    var core = require('web.core');
    var _t = core._t;


    class ReturnOrderScreen extends IndependentToOrderScreen {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('update-order-line', this.updateOrderLine);
            useListener('delete-line', this.deleteLine);
            this.state = useState({ orderlines: [] });
            this.refreshData()
        }

        get client() {
            return this.props.order ? this.props.order.get_client() : null;
        }
        get orderlines() {
            return this.state.orderlines;
        }
        get name() {
            return this.props.order.name;
        }
        get customerName() {
            return this.client ? this.client.name : " ";
        }
        get saleName() {
            return this.props.order.employee.name;
        }
        get date() {
            return moment(this.props.order.validation_date).format('YYYY-MM-DD hh:mm A');
        }
        get status() {
            return this.props.order.state;
        }
        updateOrderLine(event) {
            const { key, value, index } = event.detail;
            let { orderlines } = this.state;
            orderlines[index][key] = value;
            this.state.orderlines = orderlines;
        }
        deleteLine(event) {
            const index = event.detail;
            const orderlines = [...this.state.orderlines];
            orderlines.splice(index, 1);
            this.state.orderlines = [...orderlines];
        }
        refreshData() {
            var linesReturn = this.props.order.orderlines.models.map(line => {
                var newLine = line.clone();
                newLine.quantity = -line.quantity;
                newLine.refund_original_line_id = line.id
                return newLine;
            })
            this.state.orderlines = linesReturn;
        }
        async returnOrder() {
            const { confirmed } = await this.showPopup('ConfirmPopup', {
                title: _t('Please Confirm Return Products'),
                body: _t('Are you sure that you want to return these items?'),
            });
            if (confirmed) {
                this.env.pos.add_new_order();
                const newOrder = this.env.pos.get_order();
                this.state.orderlines.map(line => {
                    line.order = newOrder;
                    newOrder.orderlines.add(line);
                })
                newOrder.name = this.props.order.name + _t('REFUND');
                newOrder.refund_original_order_id = this.props.order.backendId;
                newOrder.test = 11;
                this.showScreen('PaymentScreen');
            }
        }
        async deleteOrder() {
            this.state.order.destroy({ reason: 'abandon' })
        }
    }
    ReturnOrderScreen.template = 'ReturnOrderScreen';

    Registries.Component.add(ReturnOrderScreen);

    return ReturnOrderScreen;
});
