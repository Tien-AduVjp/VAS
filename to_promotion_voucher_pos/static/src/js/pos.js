odoo.define('to_promotion_voucher_pos.pos', function (require) {
"use strict";
var core = require('web.core');
var _t = core._t;
//var Model = require('web.DataModel');
var web_client = require('web.web_client');
var time = require('web.time');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var popups = require('point_of_sale.popups');
var rpc = require('web.rpc');
var utils = require('web.utils');
var field_utils = require('web.field_utils');

models.load_models([
    {
    	model:  'voucher.voucher',
        fields: [],
//        domain: [['state','!=','inactivated']], 
        loaded: function(self,vouchers){
            self.vouchers = vouchers;
            self.vouchers_by_code = {};
            _.each(vouchers, function(voucher){
                self.vouchers_by_code[voucher.serial] = voucher;
            });
        },
    },
],{'after': 'product.product'});

models.load_fields('pos.payment.method',['name', 'is_cash_count', 'use_payment_terminal', 'voucher_payment']);

models.Order = models.Order.extend({
	/* ---- Payment Lines --- */
    add_voucher_paymentline: function(payment_method, value, voucher_id) {
    	if (this.get_due() == 0){
    		return;
    	}
//        this.assert_editable();
        var newPaymentline = new models.Paymentline({},{order: this, payment_method:payment_method, pos: this.pos});
        
        newPaymentline.set_amount( Math.min(this.get_due(), value) );
        newPaymentline.set_voucher_id(voucher_id);
        this.paymentlines.add(newPaymentline);
        this.select_paymentline(newPaymentline);

    },
});

models.Paymentline = models.Paymentline.extend({
	initialize: function(attributes, options) {
        this.pos = options.pos;
        this.order = options.order;
        this.amount = 0;
        this.selected = false;
        this.ticket = '';
        this.payment_status = '';
        this.card_type = '';
        this.transaction_id = '';

        if (options.json) {
            this.init_from_JSON(options.json);
            return;
        }
        this.payment_method = options.payment_method;
        if (this.payment_method === undefined) {
            throw new Error(_t('Please configure a payment method in your POS.'));
        }
        this.name = this.payment_method.name;
        this.voucher_id = 0;
    },
    
    set_voucher_id: function(voucher_id) {
    	this.voucher_id = voucher_id;
    },
    
    get_voucher_id: function() {
    	return this.voucher_id;
    },
    
    export_as_JSON: function(){
        return {
            name: time.datetime_to_str(new Date()),
            payment_method_id: this.payment_method.id,
            amount: this.get_amount(),
            payment_status: this.payment_status,
            ticket: this.ticket,
            card_type: this.card_type,
            transaction_id: this.transaction_id,
            voucher_id: this.get_voucher_id()
        };
    },
});

screens.PaymentScreenWidget.include({
	init: function(parent, options) {
        var self = this;
        this._super(parent, options);

		// This is a keydown handler that prevents backspace from
        // doing a back navigation. It also makes sure that keys that
        // do not generate a keypress in Chrom{e,ium} (eg. delete,
        // backspace, ...) get passed to the keypress handler.
        this.keyboard_keydown_handler = function(event){
        	if ($('input').is(':focus')){
        		return;
        	}
            if (event.keyCode === 8 || event.keyCode === 46) { // Backspace and Delete
                event.preventDefault();

                // These do not generate keypress events in
                // Chrom{e,ium}. Even if they did, we just called
                // preventDefault which will cancel any keypress that
                // would normally follow. So we call keyboard_handler
                // explicitly with this keydown event.
                self.keyboard_handler(event);
            }
        };
        
        // This keyboard handler listens for keypress events. It is
        // also called explicitly to handle some keydown events that
        // do not generate keypress events.
        this.keyboard_handler = function(event){
        	if ($('input').is(':focus')){
        		return;
        	}
            var key = '';

            if (event.type === "keypress") {
                if (event.keyCode === 13) { // Enter
                    self.validate_order();
                } else if ( event.keyCode === 190 || // Dot
                            event.keyCode === 110 ||  // Decimal point (numpad)
                            event.keyCode === 188 ||  // Comma
                            event.keyCode === 46 ) {  // Numpad dot
                    key = self.decimal_point;
                } else if (event.keyCode >= 48 && event.keyCode <= 57) { // Numbers
                    key = '' + (event.keyCode - 48);
                } else if (event.keyCode === 45) { // Minus
                    key = '-';
                } else if (event.keyCode === 43) { // Plus
                    key = '+';
                }
            } else { // keyup/keydown
                if (event.keyCode === 46) { // Delete
                    key = 'CLEAR';
                } else if (event.keyCode === 8) { // Backspace
                    key = 'BACKSPACE';
                }
            }

            self.payment_input(key);
            event.preventDefault();
        };

        this.pos.bind('change:selectedClient', function() {
            self.customer_changed();
        }, this);
    },
    
    // handle both keyboard and numpad input. Accepts
    // a string that represents the key pressed.
    payment_input: function(input) {
		var paymentline = this.pos.get_order().selected_paymentline;

        // disable changing amount on paymentlines with running or done payments on a payment terminal
        if (this.payment_interface && !['pending', 'retry'].includes(paymentline.get_payment_status())) {
            return;
        }
        var newbuf = this.gui.numpad_input(this.inputbuffer, input, {'firstinput': this.firstinput});

        this.firstinput = (newbuf.length === 0);

        // popup block inputs to prevent sneak editing. 
        if (this.gui.has_popup()) {
            return;
        }
        
        if (newbuf !== this.inputbuffer) {
            this.inputbuffer = newbuf;
            var order = this.pos.get_order();
            if (paymentline) {
            	if (order.selected_paymentline.voucher_id){
            		return;
            	}
                var amount = this.inputbuffer;

                if (this.inputbuffer !== "-") {
                    amount = field_utils.parse.float(this.inputbuffer);
                }

                order.selected_paymentline.set_amount(amount);
                this.order_changes();
                this.render_paymentlines();
                this.$('.paymentline.selected .edit').text(this.format_currency_no_symbol(amount));
            }
        }
    },
    
});

screens.PaymentScreenWidget.include({
	click_paymentmethods: function(id) {
		var self = this;
        var payment_method = this.pos.payment_methods_by_id[id];
        var order = this.pos.get_order();
		
		if (order.electronic_payment_in_progress()) {
		            this.gui.show_popup('error',{
		                'title': _t('Error'),
		                'body':  _t('There is already an electronic payment in progress.'),
		            });
					return;
		        }
        if (payment_method.voucher_payment){
        	self.gui.show_popup('textinput',{
        		'title':_t('Please input voucher code or scan its barcode'),
                'confirm': function(code) {
                	var voucher = self.pos.vouchers_by_code[code];
                	if (!voucher){
                		self.gui.show_popup('error',{
                            'title': _t('Voucher Invalid'),
                            'body': _t('This Voucher code is incorrect.')
                        });
                		return;
                	}
                	var p_lines = self.pos.get_order().get_paymentlines();
                	var used = false;
                	for ( var i = 0; i < p_lines.length; i++ ) {
                        if (p_lines[i].voucher_id === voucher.id) {
                        	used = true;
                            break;
                        }
                    }
                	if (used){
                		self.gui.show_popup('error',{
                            'title': _t('Voucher Invalid'),
                            'body': _t('This Voucher has been used.')
                        });
                		return;
                	}
                	var voucher_ids = [voucher.id];
                	rpc.query({
                        model: 'voucher.voucher',
                        method: 'check_voucher',
                        args: [voucher_ids],
                    })
                    .then(function(res){
                		if (res['error']){
                    		self.gui.show_popup('error',{
                                'title': _t('Voucher Invalid'),
                                'body': res['message'],
                            });
                    	}
                    	else{
                    		self.pos.get_order().add_voucher_paymentline( payment_method, res['value'], res['voucher_id']);
                	        self.reset_input();
                	        self.render_paymentlines();
                    	}
                    },function(err,event){
                        event.preventDefault();
                        self.gui.show_popup('error',{
                            'title': _t('Error: Could not Save Changes'),
                            'body': _t('Your Internet connection is probably down.'),
                        });
                    });
                },
            });
        }
        else{
            order.add_paymentline(payment_method);
            this.reset_input();

            this.payment_interface = payment_method.payment_terminal;
            if (this.payment_interface) {
                order.selected_paymentline.set_payment_status('pending');
            }

            this.render_paymentlines();
        }
    },
    
});

screens.ReceiptScreenWidget.include({
	click_next: function() {
		this.reload_voucher();
        this.pos.get_order().finalize();
    },
    
    reload_voucher: function() {
    	var self = this;
        var def  = new $.Deferred();
        rpc.query({
            model: 'voucher.voucher',
            method: 'search_read',
            args: [],
        }, {
            timeout: 3000,
            shadow: true,
        })
        .then(function(vouchers){
            	_.each(vouchers, function(voucher){
                    self.pos.vouchers_by_code[voucher.serial] = voucher;
                });
                def.resolve();
            }, function(reason){reason.event.preventDefault(); def.reject(); });
        
        return def;
    },
});

//popups.include({
//	init: function(parent, args){
//		var self = this;
//		this._super(parent, args);
//		window.document.body.addEventListener('keypress',function(event) {
//        	var key = '';
//            if (event.type === "keypress") {
//                if (event.keyCode === 13) { // Enter
//                	console.log('b');
//                	self.click_confirm();
//                	event.preventDefault();
//                }
//            }
//        });
//    },
//});

});
