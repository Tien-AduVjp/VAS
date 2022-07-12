odoo.define('to_wallet.payment_form', function (require) {
    "use strict";

    var PaymentForm = require('payment.payment_form');

    PaymentForm.include({
        start: function () {
            this._super.apply(this, arguments);
            this.$txUrl = this.$('input[name="prepare_tx_url"]');
            this.baseUrl = this.$txUrl.val();
        },

        payEvent: function (ev) {
            var $amount = this.$el.find('#payment-amount');
            if ($amount.length) {
                if (!this.el.checkValidity()) {
                    return;
                }
                var url = this.baseUrl + '?amount=' + $amount.val();
                this.$txUrl.val(url);
            }
            this._super.apply(this, arguments);
        }
    });

    return PaymentForm;
});
