odoo.define('to_pos_order_to_sales_order.pos_order_to_sales_order', function (require) {
"use strict";
var core = require('web.core');
var screens = require('point_of_sale.screens');
var _t = core._t;
var models = require('point_of_sale.models');
var rpc = require('web.rpc')
var web_client = require('web.web_client');
	
screens.PaymentScreenWidget.include({
	renderElement: function() {
		var self = this;
        this._super();
        this.$('.js_create_sales_order').click(function(){
            self.click_create_sales_order();
        });
    },        
	
    click_create_sales_order: function() {
    	var self = this;
        var order = this.pos.get_order();
        order = order.export_as_JSON();
        var fields = {};
        fields.pricelist_id = this.pos.get_order().pricelist.id;
        fields.pos_config_id = this.pos.config.id;
        fields.session_id = order['pos_session_id'];
        fields.user_id = order['user_id'];
        fields.creation_date = order['creation_date'];
        fields.partner_id = order['partner_id'];
        fields.fiscal_position_id = order['fiscal_position_id'];
        fields.lines = order['lines'];
        
        if (!order['partner_id']){
        	self.gui.show_popup('confirm',{
                'title': _t('Please select the Customer'),
                'body': _t('You need to select the customer before you can create an sales order.'),
                confirm: function(){
                    self.gui.show_screen('clientlist');
                },
            });
        	return;
        }
        return rpc.query({
            model: 'sale.order',
            method: 'create_from_ui',
            args: [fields]
        }).then(function(order_id){
            self.go_to_sales_order_view(order_id);
        },function(err,event){
            event.preventDefault();
            self.gui.show_popup('error',{
                'title': _t('Error: Could not create Sales Order'),
                'body': _t('Your Internet connection is probably down.'),
            });
        });
	},
	
	go_to_sales_order_view: function(order_id){
		var self = this;
		self.gui.show_popup('confirm',{
            'title': _t('Visit Order page'),
            'body': _t('Do you want to view this order in order page?'),
            confirm: function(){
            	self.pos.get_order().finalize();
            	window.location = window.location.origin + '/web#id='+ order_id +'&view_type=form&model=sale.order';
            },
            cancel: function(){
            	self.pos.get_order().finalize();
            }
        });
	}
});

});
