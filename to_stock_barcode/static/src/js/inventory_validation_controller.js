odoo.define('to_stock_barcode.InventoryValidationController', function (require) {
    "use strict";

    var InventoryValidationController = require('stock.InventoryValidationController');
    var ControlPanelRenderer = require('web.AbstractController');
    var core = require('web.core');
    var qweb = core.qweb;

    InventoryValidationController.include({

        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            if (!this.inventory_id) {
                var context = renderer.state.getContext();
                this.inventory_id = context.default_inventory_id;
            }
            this.barcodeCommands = {
                'O-BTN.validate': this._onValidateInventory.bind(this),
            };
            this.scan_location_id = false;
            this.scan_location = false;
        },

        start: function () {
            var self = this;
            this._barcodeStartListening();
            return this._super.apply(this, arguments).then(self._getScanLocation.bind(self));
        },

        destroy: function () {
            this._barcodeStopListening();
            this._super();
        },

        _getScanLocation: function () {
            var self = this;
            this._rpc({
                model: 'stock.inventory',
                method: 'read',
                args: [self.inventory_id, ['scan_location_id']],
            }).then(function (result) {
                var scan_location = result[0].scan_location_id;
                self.scan_location_id = scan_location[0];
                self.scan_location = scan_location[1];
                self._renderScanLocation();
            });
        },

        _renderScanLocation: function () {
            this.$buttons.find('.scan-location').remove();
            var $scanLocationDiv = $(qweb.render('InventoryLines.ScanLocation', {scan_location: this.scan_location}));
            $scanLocationDiv.appendTo(this.$buttons);
        },

        _saveScanLocation: function () {
            var self = this;
            return this._saveEditingRecord().then(function () {
                self._rpc({
                    model: 'stock.inventory',
                    method: 'write',
                    args: [self.inventory_id, {scan_location_id: self.scan_location_id}],
                });
            })
        },

        _barcodeStartListening: function () {
            core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
        },

        _barcodeStopListening: function () {
            core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
        },

        _saveEditingRecord: function () {
            var recordID = this.renderer.getEditableRecordID();
            if (recordID) {
                return this.saveRecord(recordID);
            }
            return Promise.resolve()
        },

        _onBarcodeScanned: function (barcode, target) {
            this._barcodeStopListening();
            if (barcode in this.barcodeCommands) {
                this.barcodeCommands[barcode]();
                return;
            }
            var self = this;
            return this._saveEditingRecord().then(function () {
                self._rpc({
                    model: 'stock.inventory',
                    method: 'on_validation_scanned',
                    args: [self.inventory_id, barcode]
                }).then(function (result) {
                    if (result && result.scan_location) {
                        self.scan_location_id = result.scan_location[0];
                        self.scan_location = result.scan_location[1];
                        self._saveScanLocation().then(function () {
                            self._renderScanLocation();
                            self._barcodeStartListening();
                        });
                    } else {
                        self.reload();
                        self._barcodeStartListening();
                    }
                })
            })
        },

        do_action: function (action, options) {
            // If the tracked products warning wizard displays,
            // we should stop the barcode listening until this wizard is discarded/closed
            if (action.res_model === 'stock.track.confirmation' && options && options.on_close) {
                this._barcodeStopListening();
                var self = this;
                var exitCallback = options.on_close;
                var newExitCallback = function (infos) {
                    exitCallback(infos);
                    if (infos && infos.special) {
                        self._barcodeStartListening();
                    }
                };
                options.on_close = newExitCallback;
            }
            return this._super.apply(this, arguments);
        }
    });

    ControlPanelRenderer.include({

        on_attach_callback: function () {
            // If we are on the inventory screen, don't auto focus on search input,
            // so the user can start scanning barcode immediately
            if (this.model_name === 'stock.inventory.line') {
                return;
            }
            this._super();
        },
    })
});
