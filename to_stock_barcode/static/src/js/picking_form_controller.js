odoo.define('to_stock_barcode.picking_form_controller', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var core = require('web.core');
    var _t = core._t;

    FormController.include({

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        _barcodeRecordFilter: function (record, barcode, activeBarcode) {
            var matching = this._super.apply(this, arguments);
            var data = record.data;
            if (activeBarcode.widget === 'picking_barcode_handler') {
                matching = matching && !data.location_processed && !data.result_package_id;
            }
            return matching;
        },

        _barcodeListeningAction: function (action) {
            var self = this;
            self._barcodeStopListening();
            self.do_action(action, {
                on_close: function () {
                    self._barcodeStartListening();
                    self.update({}, {reload: true});
                }
            });
        },

        _barcodeSelectedCandidate: function (candidate, record, barcode, activeBarcode) {
            if (activeBarcode.widget === 'picking_barcode_handler' && candidate.data.lots_visible) {
                var self = this;
                return this.saveRecord(this.handle, {stayInEdit: true, reload: false})
                    .then(function () {
                        return self._rpc({
                            model: 'stock.picking',
                            method: 'get_candidates_from_barcode',
                            args: [[record.data.id], barcode],
                        }).then(function (action) {
                            self._barcodeListeningAction(action);
                        });
                    });
            }
            return this._super.apply(this, arguments);
        },

        _barcodeWithoutCandidate: function (record, barcode, activeBarcode) {
            if (activeBarcode.widget === 'picking_barcode_handler') {
                var self = this;
                return this.saveRecord(this.handle, {stayInEdit: true, reload: false})
                    .then(function () {
                        return self._rpc({
                            model: 'stock.picking',
                            method: 'scan_new_product',
                            args: [[record.data.id], barcode],
                        }).then(function (action) {
                            if (action !== undefined) {
                                self._barcodeListeningAction(action);
                            } else {
                                setTimeout(function () {
                                    self.update({}, {reload: true});
                                }, 100);

                            }
                        });
                    });
            }
            return this._super.apply(this, arguments);
        },

        _barcodePickingAddRecord: function (barcode, activeBarcode) {
            if (!activeBarcode.handle) {
                return $.Deferred().reject();
            }
            var state = this.model.get(activeBarcode.handle).data.state;
            if (state === 'cancel') {
                this.do_warn(
                    _t("Picking cancelled"),
                    _t("This picking is cancelled and cannot be edited.")
                );
                return $.Deferred().reject();
            } else if (state === 'done') {
                this.do_warn(
                    _t("Picking done"),
                    _t("This picking is done and cannot be edited.")
                );
                return $.Deferred().reject();
            }
            return this._barcodeAddX2MQuantity(barcode, activeBarcode);
        }
    });

});
