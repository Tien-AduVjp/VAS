odoo.define('to_product_pos_return_reason.pos_models', function (require) {
"use strict";
var core = require('web.core');
var models = require('point_of_sale.models');

models.load_models([
    {
    	model:  'product.return.reason',
        fields: ['name','description'],
//        domain: [['customer','=',true]], 
        loaded: function(self,return_reasons){
            self.return_reasons = return_reasons;
        },
    },
],{'after': 'product.product'});

});
