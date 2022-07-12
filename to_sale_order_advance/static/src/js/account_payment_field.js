odoo.define('to_sale_order_advance.payment', function (require) {
"use strict";

var payment = require('account.payment');


payment.ShowPaymentLineWidget.include({
    _onOutstandingCreditAssign: function (event) {
        event.stopPropagation();
        event.preventDefault();
        var self = this;

        var id = $(event.target).data('id') || false;
        var outstanding_value = JSON.parse(self.value);

        var payment_with_so = false;
        if (id && outstanding_value.content) {
            for (let i=0; i < outstanding_value.content.length; i++) {
                if (outstanding_value.content[i].id == id && outstanding_value.content[i].payment_with_so) {
                    payment_with_so = true;
                }
            }
        }

        if (payment_with_so) {
            self.do_action({
                name: 'Assign To Invoice Wizard',
                res_model: 'assign.to.invoice.wizard',
                views: [[false, 'form']],
                type: 'ir.actions.act_window',
                target: 'new',
                view_mode: 'form',
                context: {'is_modal': true,
                          'move_id': outstanding_value.move_id,
                          'line_id': id,
                          },
            });
        } else {
            return this._super.apply(this, arguments);
        }
    },
});

});
