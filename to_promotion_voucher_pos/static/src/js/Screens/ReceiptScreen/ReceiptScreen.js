odoo.define('to_promotion_voucher_pos.ReceiptScreen', function (require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const PromotionReceiptScreen = (ReceiptScreen) =>
        class extends ReceiptScreen {
            orderDone() {
                this.reload_voucher();
                super.orderDone();
            }
            reload_voucher() {
                var self = this;
                this.rpc({
                    model: 'voucher.voucher',
                    method: 'search_read',
                    args: [],
                }, {
                    timeout: 3000,
                    shadow: true,
                }).then(function (vouchers) {
                    _.each(vouchers, function (voucher) {
                        self.env.pos.vouchers_by_code[voucher.serial] = voucher;
                    });
                    def.resolve();
                }, function (reason) {
                    reason.event.preventDefault();
                });

            }
        };

    Registries.Component.extend(ReceiptScreen, PromotionReceiptScreen);

    return ReceiptScreen;
});
