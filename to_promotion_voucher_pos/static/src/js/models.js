odoo.define('to_promotion_voucher_pos.models', function (require) {
    'use strict';

    const models = require('point_of_sale.models');
    var _super_paymentline = models.Paymentline;

    models.load_fields('pos.payment.method', ['name', 'is_cash_count', 'use_payment_terminal', 'voucher_payment']);

    models.load_models([
        {
            model: 'voucher.voucher',
            fields: [],
            loaded: function (self, vouchers) {
                self.vouchers = vouchers;
                self.vouchers_by_code = {};
                _.each(vouchers, function (voucher) {
                    self.vouchers_by_code[voucher.serial] = voucher;
                });
            },
        },
    ], { 'after': 'product.product' });

    models.Paymentline = models.Paymentline.extend({
        initialize: function (attributes, options) {
            this.voucher_id = 0;
            _super_paymentline.prototype.initialize.apply(this, arguments);
        },

        set_voucher_id: function (voucher_id) {
            this.voucher_id = voucher_id;
        },

        get_voucher_id: function () {
            return this.voucher_id;
        },
        init_from_JSON(json) {
            _super_paymentline.prototype.init_from_JSON.apply(this, arguments);
            this.voucher_id = json.voucher_id
        },
        export_as_JSON: function () {
            var json = _super_paymentline.prototype.export_as_JSON.apply(this, arguments);
            json.voucher_id = this.get_voucher_id();
            return json;
        },
    });
    models.Order = models.Order.extend({
        add_voucher_paymentline: function (payment_method, value, voucher_id) {
            if (this.get_due() == 0) {
                return;
            }
            var newPaymentline = new models.Paymentline({}, { order: this, payment_method: payment_method, pos: this.pos });

            newPaymentline.set_amount(Math.min(this.get_due(), value));
            newPaymentline.set_voucher_id(voucher_id);
            this.paymentlines.add(newPaymentline);
            this.select_paymentline(newPaymentline);
        },
    });
});
