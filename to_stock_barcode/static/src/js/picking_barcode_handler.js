odoo.define('to_stock_barcode.picking_barcode_handler', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');

    var PickingBarcodeHandler = AbstractField.extend({
        init: function () {
            this._super.apply(this, arguments);

            var show_reserved = this.record.data.show_reserved === false || this.record.data.show_operations === false;
            var fieldName = show_reserved ? 'move_line_nosuggest_ids' : 'move_line_ids_without_package';

            this.trigger_up('activeBarcode', {
                name: this.name,
                fieldName: fieldName,
                quantity: 'qty_done',
                notifyChange: false,
                commands: {
                    'barcode': '_barcodePickingAddRecord',
                    'O-CMD.MAIN-MENU': _.bind(this.do_action, this, 'to_stock_barcode.stock_barcode_main_action', {clear_breadcrumbs: true}),
                }
            });
        },
    });

    field_registry.add('picking_barcode_handler', PickingBarcodeHandler);

});
