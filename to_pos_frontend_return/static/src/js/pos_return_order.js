odoo.define('to_pos_frontend_return.pos_return_order', function (require) {
"use strict";
var core = require('web.core');
var chrome = require('point_of_sale.chrome');
var _t = core._t;
var models = require('point_of_sale.models');
var rpc = require('web.rpc');
var web_client = require('web.web_client');
var gui = require('point_of_sale.gui');
var screen = require('point_of_sale.screens');
var QWeb = core.qweb;

chrome.OrderSelectorWidget.include({
	manageorder_click_handler: function(event, $el) {
		this.gui.show_screen('orderlist');
    },
	renderElement: function(){
        var self = this;
        this._super();
        this.$('.manageorder-button').click(function(event){
            self.manageorder_click_handler(event,$(this));
        });
    },
});

var OrderListScreenWidget = screen.ScreenWidget.extend({
    template: 'OrderListScreenWidget',

    init: function(parent, options){
        this._super(parent, options);
        this.order_cache = new screen.DomCache();
        this.order_line_cache = new screen.DomCache();
    },

    auto_back: true,

    show: function(){
        var self = this;
        this._super();
        this.sesion_id = this.pos.db.load('pos_session_id');        

        this.renderElement();
        this.details_visible = false;

        this.$('.back').click(function(){
            self.gui.back();
        });        
        this.load_new_orders();            
    },
    after_order_load: function() {
    	var self = this;
    	var orders = this.pos.db.get_orders_sorted(1000);
    	self.render_list(orders);               
    	    	
    	self.$('.order-list-contents .order-line').off().on('click',function(event){
            self.line_select(event,$(this),parseInt($(this).data('id')));
        });    


        var search_timeout = null;

        if(self.pos.config.iface_vkeyboard && self.chrome.widget.keyboard){
        	self.chrome.widget.keyboard.connect(self.$('.searchbox input'));
        }

        self.$('.searchbox input').on('keyup',function(event){
            clearTimeout(search_timeout);
            var query = this.value;

            search_timeout = setTimeout(function(){
                self.perform_search(query,event.which === 13);
            },70);
        });

        self.$('.searchbox .search-clear').click(function(){
            self.clear_search();
        });
    },
    hide: function () {
        this._super();
    },
    perform_search: function(query, associate_result){
        var orders;
        if(query){
        	orders = this.pos.db.search_order(query);
            this.display_order_details('hide');
            if ( associate_result && orders.length === 1){
                this.gui.back();
            }
            this.render_list(orders);
        }else{
        	orders = this.pos.db.get_orders_sorted();
            this.render_list(orders);
        }
    },
    clear_search: function(){
        var orders = this.pos.db.get_orders_sorted(1000);
        this.render_list(orders);
        this.$('.searchbox input')[0].value = '';
        this.$('.searchbox input').focus();
    },
    render_list: function(orders){
        var contents = this.$el[0].querySelector('.order-list-contents');
        contents.innerHTML = "";
        for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
            var order    = orders[i];
            var line = this.order_cache.get_node(order.id);
            if(!line){
                var line_html = QWeb.render('OrderLine',{widget: this, order:orders[i]});
                var line = document.createElement('tbody');
                line.innerHTML = line_html;
                line = line.childNodes[1];
                this.order_cache.cache_node(order.id,line);
            }
            contents.appendChild(line);
        }
    },
    render_order_line_list: function(lines){
        var contents = this.$el[0].querySelector('.order-line-list-contents');
        contents.innerHTML = "";
        for(var i = 0, len = Math.min(lines.length,1000); i < len; i++){
        	var order_line    = this.pos.db.get_order_line_by_id(lines[i]);
            var taxs = order_line.tax_ids_after_fiscal_position;
            if (taxs.length > 0){
            	var new_taxs = [];
            	for (var j = 0; j < taxs.length; j++){
            		new_taxs.push(this.pos.taxes_by_id[taxs[j]].name);
            	}
            	order_line.tax_ids_name = new_taxs;
            }
            var line = this.order_line_cache.get_node(order_line.id);
            if(!line){
                var line_html = QWeb.render('OrderLineList',{widget: this, line:order_line});
                var line = document.createElement('tbody');
                line.innerHTML = line_html;
                line = line.childNodes[1];
                this.order_line_cache.cache_node(order_line.id,line);
            }
            contents.appendChild(line);
        }
    },
    render_order_return_line_list: function(lines){
        var contents = this.$el[0].querySelector('.order-line-return-list-contents');
        contents.innerHTML = "";
        var self = this;
        for(var i = 0, len = Math.min(lines.length,1000); i < len; i++){
            var order_line    = this.pos.db.get_order_line_by_id(lines[i]);
            var taxs = order_line.tax_ids_after_fiscal_position;
            if (taxs.length > 0){
            	var new_taxs = [];
            	for (var j = 0; j < taxs.length; j++){
            		new_taxs.push(this.pos.taxes_by_id[taxs[j]].name);
            	}
            	order_line.tax_ids_name = new_taxs;
            }
            var line_html = QWeb.render('OrderLineReturnList',{widget: this, line:order_line});
            var line = document.createElement('tbody');
            line.innerHTML = line_html;
            line = line.childNodes[1];
            contents.appendChild(line);
        }
        
        this.$('.order-line-return-list-contents .qty').each(function(idx,el){
        	$(this).change(function(e){
        		var line_fields = {};
        		var _self = this;
        		$(this).parent().parent().find('.return-detail').each(function(ids, els){
            		line_fields[els.name] = els.value || false;
            	})
            	rpc.query({
            		model: 'pos.order',
            		method: 'onchange_qty_from_ui',
            		args: [line_fields]            	
                }).then(function(total){
            		if (total.length > 0){
            			$(_self).parent().parent().find('.price_subtotal').val(total[0]);
            			$(_self).parent().parent().find('.price_subtotal_incl').val(total[1]);
            		}
                },function(err,event){
                    event.preventDefault();
                    self.gui.show_popup('error',{
                        'title': _t('Error: Could not Save Changes'),
                        'body': _t('Your Internet connection is probably down.'),
                    });
                });
        	});
    	});        
        
        this.$('.order-line-return-list-contents .return-detail').each(function(idx,el){
        	$(this).keydown(function(event){
        		var regex = new RegExp("^[0-9\.\b\-]+$");
        	    var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        	    if (!regex.test(key) && key != '%' && key != "'") {
        	       event.preventDefault();
        	       return false;
        	    }
        	});
        });
    },
    line_select: function(event,$line,id){
        var order = this.pos.db.get_order_by_id(id);
        this.$('.order-list .lowlight').removeClass('lowlight');
        if ( $line.hasClass('highlight') ){
            $line.removeClass('highlight');
            $line.addClass('lowlight');
            this.display_order_details('hide',order);
            this.new_order = null;
//            this.toggle_save_button();
        }else{
            this.$('.order-list .highlight').removeClass('highlight');
            $line.addClass('highlight');
            var y = event.pageY - $line.parent().offset().top;
            this.display_order_details('show',order,y);
            this.new_order = order;
//            this.toggle_save_button();
        }
    },
    
    view_return_order_details: function(order) {
    	//check Expiration
    	var date_order = new Date(order.date_order).getTime();
    	var now = new Date().getTime();
    	var expiry_date = new Date(date_order + this.pos.config.nod_return_product*1000*60*60*24)
    	var period = (now - date_order)/(1000*60*60*24);
    	if (period > this.pos.config.nod_return_product && this.pos.config.nod_return_product) {
            this.gui.show_popup('error',_.str.sprintf(_t('This order has exceeded the maximum number of days for return. Its return should have been done before %s'),expiry_date));
            return;
        }
        this.display_order_details('return',order);
        
    },
    
    view_payment_order: function(order) {
    	this.display_order_details('payment', order);
    },

    // what happens when we save the changes on the client edit form -> we fetch the fields, sanitize them,
    // send them to the backend for update, and call saved_client_details() when the server tells us the
    // save was successfull.
    save_return_order_details: function(order) {
        var self = this;
        //Check returnable product
        var fields = {};
        var lines = [];
        this.$('.order-line-return-list-contents .return-list').each(function(idx,el){
        	var line_fields = {};
        	$(this).find('.return-detail').each(function(ids, els){
        		line_fields[els.name] = els.value || false;
        	})
        	lines.push(line_fields);
        });
        fields['lines'] = lines;
        fields['partner_id'] = order.partner_id[0] || false;
        fields['session_id'] = order.session_id[0] || false;
        fields['fiscal_position_id'] = order.fiscal_position_id[0] || false;
        fields['date_order'] = (new Date()).toLocaleString();
        fields['user_id'] = this.pos.user.id;
        fields['pos_reference'] = order.pos_reference;
        fields['refund_original_order_id'] = order.id;
        
        this.gui.show_popup('confirm',{
            title: _t('Please Confirm Return Products'),
            body:  _t('Are you sure that you want to return these items?'),
            confirm: function() {
            	rpc.query({
            		model: 'pos.order',
            		method: 'create_return_order_from_ui',
            		args: [fields]            	
                }).then(function(value){
            		if (value['invalid_product'].length > 0){
            			self.$('.order-line-return-list-contents .return-list').each(function(i,e){
            				if ($.inArray($(this).data('product-id'), value['invalid_product']) !== -1){
            					$(this).addClass('error');
            				}
            			});
            			this.gui.show_popup('error',_t('Some products in this order are not returnable.'));
            		}
            		else{
            			self.saved_order_details(value['order_id']);
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
    },
    
 // what happens when we've just pushed modifications for a partner of id partner_id
    saved_order_details: function(order_id){
    	var self = this;
        var def  = new $.Deferred();                       
        if(this.pos.config.nod_return_product){
        	var date = new Date();
        	date.setDate(date.getDate() - this.pos.config.nod_return_product);
        	var new_date = date.getFullYear() + '/' + (date.getMonth() + 1) + '/' + date.getDate() + ' ' + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds()
            var domain = [['session_id.config_id.id','=',this.pos.config.id],['date_order','>',new_date]];
        }                      
        else{
        	var domain = [['session_id.id','=',this.sesion_id]];
        }
        rpc.query({
                model: 'pos.order',
                method: 'search_read',
                args: [domain, []],
            }, {
                timeout: 3000,
                shadow: true,
            }).then(function(orders){            	
                if (self.pos.db.add_orders(orders)) {   // check if the orders we got were real updates                	
                	var order_line_fields = ['product_id','qty','price_unit','discount','tax_ids_after_fiscal_position','tax_ids','price_subtotal','price_subtotal_incl', 'order_id', 'write_date'];
                	if(self.pos.config.nod_return_product){
                		var domain = [['order_id.session_id.config_id.id','=',self.pos.config.id],['write_date','>',new_date]];
                	}
                	else{
                		var domain = [['order_id.session_id.id','=',self.sesion_id]];
                	}
                    rpc.query({
                            model: 'pos.order.line',
                            method: 'search_read',
                            args: [domain, order_line_fields],
                        }, {
                            timeout: 3000,
                            shadow: true,
                        }).then(function(lines){
                        if (self.pos.db.add_orderlines(lines)) {   // check if the orders we got were real updates
                        	var order = self.pos.db.order_by_id[order_id];
                            if (order) {
                                self.display_order_details('show',order);
                            } else {
                                // should never happen, because create_from_ui must return the id of the partner it
                                // has created, and reload_partner() must have loaded the newly created partner. 
                                self.display_order_details('hide');
                            }                            
                            self.after_order_load();
                            def.resolve();
                        } else {
                            def.reject();
                        }
                    }, function(err,event){ event.preventDefault(); def.reject(); });                     
                } else {
                    def.reject();
                }
            }, function(err,event){ event.preventDefault(); def.reject(); });
        //load new order line
    },

    
    save_payment_order: function(order){    	
    	var self = this;
    	var fields = {};
    	this.$('.order-details-contents .paymentx').each(function(idx,el){
            fields[el.name] = el.value || false;
        });
    	if (!fields.journal_id) {
            this.gui.show_popup('error',_t('A Payment method Is Required'));
            return;
        }
    	if (!fields.amount || fields.amount != fields.amount_total){
    		this.gui.show_popup('error',_t('The payment amount must match the amount total in order'));
            return;
    	}
    	rpc.query({
    		model: 'pos.order',
    		method: 'create_payment_from_ui',
    		args: [fields]          	
        }).then(function(){
            self.saved_order_details(order.id);
        },function(error){
            error.event.preventDefault();
            self.gui.show_popup('error',{
                'title': _t('Error: Could not Save Changes'),
                'body': _t('Your Internet connection is probably down.'),
            });
        });
    },
    
    
    load_new_orders: function(){    	
        var self = this;
        var def  = new $.Deferred();        
        if(this.pos.config.nod_return_product){
        	var date = new Date();
        	date.setDate(date.getDate() - this.pos.config.nod_return_product);
        	var new_date = date.getFullYear() + '/' + (date.getMonth() + 1) + '/' + date.getDate() + ' ' + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds()
            var domain = [['session_id.config_id.id','=',this.pos.config.id],['date_order','>',new_date]];
        }                      
        else{
        	var domain = [['session_id.id','=',this.sesion_id]];
        }        
        rpc.query({
	            model: 'pos.order',
	            method: 'search_read',
	            args: [domain, []],
	        }, {
	            timeout: 3000,
	            shadow: true,
	        }).then(function(orders){	 	        	
                if (self.pos.db.add_orders(orders)) {                	  
                	var order_line_fields = ['product_id','qty','price_unit','discount','tax_ids_after_fiscal_position','tax_ids','price_subtotal','price_subtotal_incl', 'order_id', 'write_date'];                		
                	if(self.pos.config.nod_return_product){
                		var domain = [['order_id.session_id.config_id.id','=',self.pos.config.id],['write_date','>',new_date]];
                	}
                	else{
                		var domain = [['order_id.session_id.id','=',self.sesion_id]];
                	}
                    rpc.query({
            	            model: 'pos.order.line',
            	            method: 'search_read',
            	            args: [domain, order_line_fields],
            	        }, {
            	            timeout: 3000,
            	            shadow: true,
            	        }).then(function(lines){
                        if (self.pos.db.add_orderlines(lines)) {   // check if the orders we got were real updates                        	                        	
                        	self.after_order_load();
                            def.resolve();
                        } else {
                            def.reject();
                        }
                    }, function(err,event){ event.preventDefault(); def.reject(); });                            
                } else {
                    def.reject();
                }
            }, function(err,event){ event.preventDefault(); def.reject(); });                
        return def;
    },

    
 // ui handle for the 'cancel order edit changes' action
    undo_return_order_details: function(order) {
        if (!order.id) {
            this.display_order_details('hide');
        } else {
            this.display_order_details('return',order);
        }
    },
    
    undo_payment_order: function(order) {
    	this.display_order_details('show', order);
    },
    
    // Shows,hides or edit the customer details box :
    // visibility: 'show', 'hide' or 'edit'
    // partner:    the partner object to show or edit
    // clickpos:   the height of the click on the list (in pixel), used
    //             to maintain consistent scroll.
    display_order_details: function(visibility,order,clickpos){
        var self = this;
        var contents = this.$('.order-details-contents');
        var parent   = this.$('.order-list').parent();
        var scroll   = parent.scrollTop();
        var height   = contents.height();
        
        contents.off('click','.button.xpayment');
        contents.off('click','.button.return'); 
        contents.off('click','.button.save'); 
        contents.off('click','.button.undo'); 
        contents.off('click','.button.detele');
        contents.off('click', '.button.undo-payment');
        contents.off('click', '.button.save-payment');
        contents.on('click','.button.xpayment',function(){self.view_payment_order(order);});
        contents.on('click','.button.return',function(){ self.view_return_order_details(order); });
        contents.on('click','.button.delete',function(el){$(this).parent().parent().remove();});
        contents.on('click','.button.save',function(){ self.save_return_order_details(order); });
        contents.on('click','.button.undo',function(){ self.undo_return_order_details(order); });
        contents.on('click','.button.save-payment',function(){ self.save_payment_order(order); });
        contents.on('click','.button.undo-payment',function(){ self.undo_payment_order(order); });
//        this.editing_client = false;
//        this.uploaded_picture = null;

        if(visibility === 'show'){
            contents.empty();
            contents.append($(QWeb.render('OrderDetails',{widget:this,order:order})));
            this.render_order_line_list(order.lines);
            var new_height   = contents.height();

            if(!this.details_visible){
                // resize client list to take into account client details
                parent.height('-=' + new_height);

                if(clickpos < scroll + new_height + 20 ){
                    parent.scrollTop( clickpos - 20 );
                }else{
                    parent.scrollTop(parent.scrollTop() + new_height);
                }
            }else{
                parent.scrollTop(parent.scrollTop() - height + new_height);
            }

            this.details_visible = true;
          
        } else if (visibility === 'hide') {
            contents.empty();
            parent.height('100%');
            if( height > scroll ){
                contents.css({height:height+'px'});
                contents.animate({height:0},400,function(){
                    contents.css({height:''});
                });
            }else{
                parent.scrollTop( parent.scrollTop() - height);
            }
            this.details_visible = false;
//            this.toggle_save_button();
        } else if (visibility === 'return') {
//            this.editing_client = true;
            contents.empty();
            contents.append($(QWeb.render('OrderDetailsReturn',{widget:this,order:order})));
            this.render_order_return_line_list(order.lines);
//            this.toggle_save_button();

            // Browsers attempt to scroll invisible input elements
            // into view (eg. when hidden behind keyboard). They don't
            // seem to take into account that some elements are not
            // scrollable.
            contents.find('input').blur(function() {
                setTimeout(function() {
                    self.$('.window').scrollTop(0);
                }, 0);
            });
        }else if (visibility === 'payment') {
        	contents.empty();
        	contents.append($(QWeb.render('OrderDetailsPayment',{widget:this,order:order})));
        } 
    },
    close: function(){
        this._super();
    },
});
gui.define_screen({name:'orderlist', widget: OrderListScreenWidget});

return OrderListScreenWidget;
});
