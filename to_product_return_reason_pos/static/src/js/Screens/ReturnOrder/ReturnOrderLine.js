odoo.define('to_product_return_reason_pos.ReturnOrderLine', function (require) {
    'use strict';

    const ReturnOrderLine = require('to_pos_frontend_return.ReturnOrderLine');
    const Registries = require('point_of_sale.Registries');

    const ReasonReturnOrderLine = (ReturnOrderLine) =>
        class extends ReturnOrderLine {
            onChangeReturnReason(event) {
                this.trigger('update-order-line', { key: 'return_reason_id', value: event.target.value, index: this.props.index });
            }
            updateOtherReason(event) {
                this.trigger('update-order-line', { key: 'return_reason_orther', value: event.target.value, index: this.props.index });
            }
            get return_reasons() {
                return this.props.return_reasons;
            }
            get showNewReason() {
                return this.props.line.return_reason_id == -1;
            }
        }
    Registries.Component.extend(ReturnOrderLine, ReasonReturnOrderLine);
    return ReturnOrderLine;
});
