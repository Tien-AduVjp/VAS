odoo.define('to_stock_barcode.lot_barcode_handler', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');

    var LotBarcodeHandler = AbstractField.extend({
        init: function () {
            this._super.apply(this, arguments);

            this.trigger_up('activeBarcode', {
                name: this.name,
                fieldName: 'produce_line_ids',
                quantity: 'product_qty',
                setQuantityWithKeypress: true,
                commands: {
                    'O-CMD.MAIN-MENU': _.bind(this.do_action, this, 'to_stock_barcode.stock_barcode_main_action', {clear_breadcrumbs: true}),
                    barcode: '_barcodeAddX2MQuantity',
                }
            });
        },
    });

    field_registry.add('lot_barcode_handler', LotBarcodeHandler);

});
