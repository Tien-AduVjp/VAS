odoo.define('to_stock_barcode.barcode_main_menu', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var Dialog = require('web.Dialog');
    var Session = require('web.session');
    var core = require('web.core');
    var _t = core._t;

    var BarcodeMainMenu = AbstractAction.extend({
        template: 'barcode_main_menu',

        events: {
            "click .o_button_operations": 'clickButtonOperations',
            "click .o_button_inventory": 'clickButtonInventory',
        },

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.message_demo = action.params.message_demo;
        },

        start: function () {
            var self = this;
            if (self.message_demo) {
                self.setup_message_demo();
            }
            return this._super();
        },

        destroy: function () {
            core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
            this._super();
        },

        on_attach_callback: function () {
            core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
        },

        on_detach_callback: function () {
            core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
        },

        setup_message_demo: function () {
            var self = this;
            self.$(".message_demo .close").on('click', function () {
                var message = _t("Do you want to remove this message?\
                It won't appear anymore, so make sure you don't need the barcodes sheet or you already have a copy.");
                Dialog.confirm(self, message, {
                    title: _t("Warning"),
                    size: 'medium',
                    buttons: [
                        {
                            text: _t("Remove it"),
                            close: true,
                            classes: 'btn-primary',
                            click: function () {
                                Session.rpc('/stock_barcode/hide_message_demo');
                                $('.alert').alert('close');
                            }
                        },
                        {
                            text: _t("Leave it"),
                            close: true
                        },
                    ],
                });
            });
        },

        clickButtonOperations: function () {
            this.do_action('to_stock_barcode.stock_picking_type_kanban_action');
        },

        clickButtonInventory: function () {
            var self = this;
            return this._rpc({
                model: 'stock.inventory',
                method: 'open_new_inventory',
            })
                .then(function (result) {
                    self.do_action(result);
                });
        },

        _onBarcodeScanned: function (barcode) {
            if (document.readyState !== 'complete') {
                return;
            }
            var self = this;
            Session.rpc('/stock_barcode/main_menu_scan', {barcode: barcode})
                .then(function (result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
        },
    });

    core.action_registry.add('to_barcode_main_action', BarcodeMainMenu);

    return {BarcodeMainMenu: BarcodeMainMenu};

});
