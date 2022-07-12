odoo.define('to_promotion_voucher_pos.PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    var core = require('web.core');
    var _t = core._t;
    const NumberBuffer = require('point_of_sale.NumberBuffer');

    const PromotionPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            async addNewPaymentLine({ detail: paymentMethod }) {
                if (paymentMethod.voucher_payment) {
                    self = this;
                    const { confirmed, payload: code } = await this.showPopup('TextInputPopup', {
                        title: _t('Please input voucher code or scan its barcode'),
                        confirmText: _t('OK'),
                        cancelText: _t('Cancel')
                    });
                    if (confirmed) {
                        var voucher = this.env.pos.vouchers_by_code[code];
                        if (!voucher) {
                            this.showPopup('ErrorPopup', {
                                title: _t('Voucher Invalid'),
                                body: _t('This Voucher code is incorrect.')
                            });
                            return;
                        }

                        var oders = this.env.pos.get_order_list()
                        var p_lines = [];
                        oders.map(order => {
                            p_lines.push.apply(p_lines, order.get_paymentlines())
                        })
                        var used = false;
                        for (var i = 0; i < p_lines.length; i++) {
                            if (p_lines[i].voucher_id === voucher.id) {
                                used = true;
                                break;
                            }
                        }
                        if (used) {
                            this.showPopup('ErrorPopup', {
                                title: _t('Voucher Invalid'),
                                body: _t('This Voucher has been used.')
                            });
                            return;
                        }
                        var voucher_ids = [voucher.id];
                        this.rpc({
                            model: 'voucher.voucher',
                            method: 'check_voucher',
                            args: [voucher_ids],
                        })
                            .then(function (res) {
                                if (res['error']) {
                                    self.showPopup('ErrorPopup', {
                                        title: _t('Voucher Invalid'),
                                        body: res['message'],
                                    });
                                }
                                else {
                                    self.currentOrder.add_voucher_paymentline(paymentMethod, res['value'], res['voucher_id']);
                                    NumberBuffer.reset();
                                }
                            }, function (err, event) {
                                event.preventDefault();
                                self.showPopup('ErrorPopup', {
                                    title: _t('Error: Could not Save Changes'),
                                    body: _t('Your Internet connection is probably down.'),
                                });
                            });
                    }
                } else {
                    super.addNewPaymentLine({ detail: paymentMethod });
                }
            }
        };

    Registries.Component.extend(PaymentScreen, PromotionPaymentScreen);

    return PaymentScreen;
});
