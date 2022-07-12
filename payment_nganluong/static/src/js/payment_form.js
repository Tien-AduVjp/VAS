odoo.define('payment_nganluong.payment_form', function(require) {
	"use strict";

	var PaymentForm = require('payment.payment_form');
	PaymentForm.include({
		updateNewPaymentDisplayStatus : function(ev) {
			this._super(ev);
			var checked_radio = this.$('input[type="radio"]:checked');
			if (checked_radio.attr('data-provider') == 'nganluong') {
				this.$('div#nganluong_fees_active').show();
			} else {
				this.$('div#nganluong_fees_active').hide();
			}
		},
	});
	return PaymentForm;
});
