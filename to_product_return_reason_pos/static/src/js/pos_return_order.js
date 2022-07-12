odoo.define('to_product_pos_return_reason.pos_return_order', function (require) {
"use strict";
var core = require('web.core');
var models = require('point_of_sale.models');
var rpc = require('web.rpc')
var gui = require('point_of_sale.gui');
var pos_return_order = require('to_pos_frontend_return.pos_return_order');
var _t = core._t;
var QWeb = core.qweb;

pos_return_order.include({
	
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
        contents.on('click','.button.undo-payment',function(){ self.undo_payment_order(order); });
        contents.on('click','.button.save-payment',function(){ self.save_payment_order(order); });
        if(this.pos.config.allow_to_create_new_reason != false){
        	contents.off('change','.order-line-return-reason');
        	contents.on('change','.order-line-return-reason',function(){ self.change_return_reason(); });
        	/*this.$('.new_return_reason').each(function(idx,el){
            	$(this).off();
            });*/
        }
        else{
        	contents.off('focus','.order-line-return-reason');
        	contents.on('focus','.order-line-return-reason',function(){ self.change_return_reason(); });
        }

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
            this.$('.order-line-return-list-contents .return-detail.new_return_reason').each(function(idx,el){
            	$(this).off('keydown').keydown(function(event){
            		return true;
            	});
            });
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

    change_return_reason: function(){
    	if(this.pos.config.allow_to_create_new_reason != false){
        	$('.other_reason').show();
        }
        else{
        	$('.other_reason').hide();
        }
    	$('.order-line-return-reason').each(function() {
    		  if($(this).val() != -1){
    			  $(this).parent().find('.new_return_reason').val('').hide();
    		  }
    		  else{
    			  $(this).parent().find('.new_return_reason').show().focus();
    		  }
    	});
    },
	
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
        fields['return_reason_id'] = this.$('.order-details-box').find('select.order-return-reason').val();
        
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
            			self.gui.show_popup('error',_t('Some products in this order are not returnable.'));
            		}
            		else if(value['invalid_order'] == 1){
            			self.gui.show_popup('error',value['order_error']);
            		}
            		else{
            			self.saved_order_details(value['order_id']);
            		}
                }).catch(function(err){
                    err.event.preventDefault();                    
                    self.loading_error(err);
                });
            },
        });
    },
    loading_error: function(err){
        var self = this;

        var title = err.message;
        var body  = err.stack;

        if(err.message === 'XmlHttpRequestError '){
            title = _t('Network Failure (XmlHttpRequestError)');
            body  = _t('The Point of Sale could not be loaded due to a network problem.\n Please check your internet connection.');
        }else if(err.code === 200){
            title = err.data.message;
            body  = err.data.debug;
        }

        if( typeof body !== 'string' ){
            body = _t('Traceback not available.');
        }

        self.gui.show_popup('error',{
            'title': title,
            'body': body,
        });
    },
});

});
