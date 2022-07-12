odoo.define('to_pos_delivery.pos_delivery', function (require) {
"use strict";
var core = require('web.core');
var screens = require('point_of_sale.screens');
var _t = core._t;
var models = require('point_of_sale.models');
var rpc = require('web.rpc')
var web_client = require('web.web_client');
var time = require('web.time');

models.load_models([
    {
        model: 'delivery.carrier',
        fields: ['name','delivery_type'],
        loaded: function(self,deliveries){ 
            self.deliveries = deliveries; 
        },
    },
],{'after': 'product.product'});

models.Order = models.Order.extend({
    set_to_delivery: function(to_delivery){
        this.assert_editable();
        this.to_delivery = to_delivery;
    },
    is_to_delivery: function(){
    	if (this.to_delivery === undefined){
    		this.to_delivery = false;
    	}
        return this.to_delivery;
    }
});

models.PosModel = models.PosModel.extend({
	_save_to_server: function (orders, options) {
        if (!orders || !orders.length) {
            var result = $.Deferred();
            result.resolve([]);
            return result;
        }
        options = options || {};

        var self = this;
        var timeout = typeof options.timeout === 'number' ? options.timeout : 7500 * orders.length;

        // Keep the order ids that are about to be sent to the
        // backend. In between create_from_ui and the success callback
        // new orders may have been added to it.
        var order_ids_to_sync = _.pluck(orders, 'id');

        // we try to send the order. shadow prevents a spinner if it takes too long. (unless we are sending an invoice,
        // then we want to notify the user that we are waiting on something )    
		   
        var args = [_.map(orders, function (order) {
            order.to_invoice = options.to_invoice || false;
            order.data.to_delivery = options.to_delivery || false;
            var delivery_method = $('.input-delivery-method').val();
            //var delivery_date = $('.input-year').val() + '-' + $('.input-month').val() + '-' + $('.input-day').val() + ' ' + $('.input-hour').val() + ':' + $('.input-minute').val() + ':00';
			var dt = new Date();
			var year = dt.getFullYear();
            var month = dt.getMonth()+1;
            var day = dt.getDate();
            var hour = dt.getHours();
            var minute = dt.getMinutes();
            month = (month<10 ? '0' : '') + month;
            day = (day<10 ? '0' : '') + day;
            hour = (hour<10 ? '0' : '') + hour;
            minute = (minute<10 ? '0' : '') + minute;
			var new_date = $('.input-date').val() != '' ? $('.input-date').val() : year + '-' + month + '-' + day;
			var new_time = $('.input-time').val() != '' ? $('.input-time').val() : hour + ':' + minute;
			var delivery_date = new_date + ' ' +new_time + ':' + '00';
			//var delivery_date = '';
            order.data.carrier_id = delivery_method != '' ? parseInt(delivery_method) : false;
            order.data.delivery_date = delivery_date;
            return order;
        })];
        args.push(options.draft || false);
        return rpc.query({
            model: 'pos.order',
            method: 'create_from_ui',
            args: args,
        }, {
        	shadow: !options.to_invoice,
            timeout: timeout
        }).then(function (server_ids) { 
        	 _.each(order_ids_to_sync, function (order_id) {
                 self.db.remove_order(order_id);
             });
             self.set('failed',false);
             
             return server_ids;
        }).catch(function (reason){
            var error = reason.message;
            if(error.code === 200 ){    // Business Logic Error, not a connection problem
                //if warning do not need to display traceback!!
                if (error.data.exception_type == 'warning') {
                    delete error.data.debug;
                }

                // Hide error if already shown before ...
                if ((!self.get('failed') || options.show_error) && !options.to_invoice) {
                    self.gui.show_popup('error-traceback',{
                        'title': error.data.message,
                        'body':  error.data.debug
                    });
                }
                self.set('failed',error);
            }
            // prevent an error popup creation by the rpc failure
            // we want the failure to be silent as we send the orders in the background
           // event.preventDefault();
            console.error('Failed to send orders:', orders);

        });       
    },
});        
screens.PaymentScreenWidget.include({

    init: function(parent, options) {
        var self = this;
        this._super(parent, options);

        this.pos.bind('change:selectedOrder',function(){
                this.renderElement();
                this.watch_order_changes();
            },this);
        this.watch_order_changes();

        this.inputbuffer = "";
        this.firstinput  = true;
        this.decimal_point = _t.database.parameters.decimal_point;
        
        // This is a keydown handler that prevents backspace from
        // doing a back navigation. It also makes sure that keys that
        // do not generate a keypress in Chrom{e,ium} (eg. delete,
        // backspace, ...) get passed to the keypress handler.
        this.keyboard_keydown_handler = function(event){
        	if ($('.input-time').is(':focus')){
        		return
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
        	if ($('.input-time').is(':focus')){
        		return
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

	renderElement: function() {
		var self = this;
        this._super();
        this.$('.js_delivery').click(function(){
            self.click_set_delivery();
        });
    },
    
    click_set_delivery: function() {
    	var order = this.pos.get_order();
        order.set_to_delivery(!order.is_to_delivery());
        if (order.is_to_delivery()) {
            this.$('.js_delivery').addClass('highlight');
            this.$('.input-delivery').removeClass('hidden');
            var dt = new Date();
			var year = dt.getFullYear();
            var month = dt.getMonth()+1;
            var day = dt.getDate();
            var hour = dt.getHours();
            var minute = dt.getMinutes();
            month = (month<10 ? '0' : '') + month;
            day = (day<10 ? '0' : '') + day;
            hour = (hour<10 ? '0' : '') + hour;
            minute = (minute<10 ? '0' : '') + minute;
			var date = year + '-' + month + '-' + day
			var time = hour + ':' + minute
			this.$('.input-date').val(date);
			this.$('.input-time').val(time);
			var payment_line = this.$('.paymentline.selected');
			var cid = payment_line.find('td.delete-button').data('cid');
			payment_line.attr('data-cid', cid);
			payment_line.removeClass('selected');
        } else {
            this.$('.js_delivery').removeClass('highlight');
            this.$('.input-delivery').addClass('hidden');
        }
    },

	payment_input: function(input) {
		if (this.$('.input-date').is(":focus") || this.$('.input-time').is(":focus")){
			return;
		}
		this._super(input);
	},
    
    finalize_validation: function() {
    	var self = this;
        var order = this.pos.get_order();

        if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) { 

                this.pos.proxy.open_cashbox();
        }

        order.initialize_validation_date();

        if (order.is_to_invoice()) {
            var invoiced = this.pos.push_and_invoice_order(order);
            this.invoicing = true;

            invoiced.catch(this._handleFailedPushForInvoice.bind(this, order, false));
            invoiced.then(function (server_ids) {
                self.invoicing = false;
                var post_push_promise = [];
                post_push_promise = self.post_push_order_resolve(order, server_ids);
                post_push_promise.then(function () {
                        self.gui.show_screen('receipt');
                }).catch(function (error) {
                    self.gui.show_screen('receipt');
                    if (error.message === 'Missing Customer') {
                        self.gui.show_popup('confirm',{
                            'title': _t('Please select the Customer'),
                            'body': _t('You need to select the customer before you can invoice an order.'),
                            confirm: function(){
                                self.gui.show_screen('clientlist');
                            },
                        });
                    } else if (error) {
                        self.gui.show_popup('error',{
                            'title': "Error: no internet connection",
                            'body':  error,
                        });
                    } else if (error.code === 200) {
                        self.gui.show_popup('error-traceback',{
                            'title': error.data.message || _t("Server Error"),
                            'body': error.data.debug || _t('The server encountered an error while receiving your order.'),
                        });
                    } else {
                        self.gui.show_popup('error',{
                            'title': _t("Unknown Error"),
                            'body':  _t("The order could not be sent to the server due to an unknown error"),
                        });
                    }
                });
            });
        }
        else if (order.is_to_delivery()) {
        	if(!order.get_client()){
        		self.gui.show_popup('confirm',{
                    'title': _t('Please select the Customer'),
                    'body': _t('You need to specify the customer before you can create a delivery for this order.'),
                    confirm: function(){
                        self.gui.show_screen('clientlist');
                    },
                });
            } 
        	else if (this.pos.config.picking_type_id == false){
        		self.gui.show_popup('error',{
                    'title': _t('The order could not be processed!'),
                    'body': _t('You are trying to create delivery for this order, but picking type in PoS config has not been set.'),
                });
        	}
        	else{
        		this.pos.push_order(order, {'to_delivery': true});
                this.gui.show_screen('receipt');
        	}
        }
        else {
            var ordered = this.pos.push_order(order);
            if (order.wait_for_push_order()){
                var server_ids = [];
                ordered.then(function (ids) {
                  server_ids = ids;
                }).finally(function() {
                    var post_push_promise = [];
                    post_push_promise = self.post_push_order_resolve(order, server_ids);
                    post_push_promise.then(function () {
                            self.gui.show_screen('receipt');
                        }).catch(function (error) {
                          self.gui.show_screen('receipt');
                          if (error) {
                              self.gui.show_popup('error',{
                                  'title': "Error: no internet connection",
                                  'body':  error,
                              });
                          }
                        });
                  });
            }
            else {
              self.gui.show_screen('receipt');
            }

        }
    }
    
});

});
