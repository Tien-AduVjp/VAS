odoo.define('to_pos_frontend_return.pos_db', function (require) {
"use strict";
var core = require('web.core');
var PosDB = require('point_of_sale.DB');

PosDB.include({
	init: function(options){
		this._super();
		this.order_sorted = [];
        this.order_by_id = {};
        this.order_search_string = "";
        this.order_write_date = null;
        this.order_line_sorted = [];
        this.order_line_by_id = {};
        this.order_line_write_date = null;
	},
	_order_search_string: function(order){
        var str =  order.name;
        if(order.refund_original_order_id) {
            str += '|' + order.refund_original_order_id[1];
        }
        if(order.partner_id){
        	str += '|' + order.partner_id[1];
        }
        if(order.pos_reference){
        	str += '|' + order.pos_reference;
        }
        str = '' + order.id + ':' + str.replace(':','') + '\n';
        return str;
    },
    add_orders: function(orders){    
        var order;
        for(var i = 0, len = orders.length; i < len; i++){
            order = orders[i];
            var search_string = this._order_search_string(order);
            this.order_search_string += search_string;
            if (!this.order_by_id[order.id]) {
                this.order_sorted.push(order.id);
            }
            this.order_by_id[order.id] = order;            
        }               
        return this.order_sorted.length;
    },
    get_order_write_date: function(){
        return this.order_write_date || "1970-01-01 00:00:00";
    },
    get_order_by_id: function(id){
        return this.order_by_id[id];
    },
    get_orders_sorted: function(max_count){
        max_count = max_count ? Math.min(this.order_sorted.length, max_count) : this.order_sorted.length;        
        var orders = [];
        for (var i = 0; i < max_count; i++) {
            orders.push(this.order_by_id[this.order_sorted[i]]);
        }
        return orders;
    },
    search_order: function(query){
        try {
            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
            query = query.replace(' ','.+');
            var re = RegExp("([0-9]+):.*?"+query,"gi");
        }catch(e){
            return [];
        }
        var results = [];
        for(var i = 0; i < this.limit; i++){
            var r = re.exec(this.order_search_string);
            if(r){
                var id = Number(r[1]);
                results.push(this.get_order_by_id(id));
            }else{
                break;
            }
        }
        return results;
    },
    add_orderlines: function(lines){                
        var line;
        for(var i = 0, len = lines.length; i < len; i++){
            line = lines[i];
            this.order_line_by_id[line.id] = line;            
        }
        return this.order_line_by_id;
    },
    get_order_line_write_date: function(){
        return this.order_line_write_date || "1970-01-01 00:00:00";
    },
    get_order_line_by_id: function(id){
        return this.order_line_by_id[id];
    },
});

});