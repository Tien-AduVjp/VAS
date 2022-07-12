odoo.define('to_pos_note.pos_note', function (require) {
"use strict";
var core = require('web.core');
var screens = require('point_of_sale.screens');
var _t = core._t;
var models = require('point_of_sale.models');
	
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
        	if ($('.pay-note').is(':focus')){
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
        	if ($('.pay-note').is(':focus')){
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
    }
});
var _super = models.Order;
models.Order = models.Order.extend({
	export_for_printing: function(){
        var json = _super.prototype.export_for_printing.apply(this,arguments);
        var note = $('.pay-note').val();
        json.note = {
            note: note, 
        };
        return json;
    },

    export_as_JSON: function(){
        var json = _super.prototype.export_as_JSON.apply(this,arguments);
        var note = $('.pay-note').val();
        json.note = note;
        return json;
    },
});

});
