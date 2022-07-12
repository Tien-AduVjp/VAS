odoo.define('to_pos_note.PosNoteOrder', function (require) {
"use strict";
var core = require('web.core');
var models = require('point_of_sale.models');
var _super = models.Order;

models.Order = models.Order.extend({
	note: null,
	export_for_printing: function(){
        var json = _super.prototype.export_for_printing.apply(this,arguments);
		 if (!this.note) {
			this.note = $('.pay-note').val();
		}
		json.note =  this.note;
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
