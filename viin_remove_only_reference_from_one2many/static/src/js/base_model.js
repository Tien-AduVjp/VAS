odoo.define('viin_remove_only_reference_from_one2many.remove_reference', function(require){
	"use strict";
	var BasicModel = require('web.BasicModel');

	BasicModel.include({
		_generateChanges: function (record, options){
			var changes = this._super(record, options);
			var fields = record.fields;
			var form = record.fieldsInfo?.form;
			if (form){
				for (var field in changes){
					if (form[field] === undefined) continue;
					var effect = JSON.parse((form[field].effect || "{}").replace(/'/g,"\""));
					if (effect && fields[field].type == 'one2many' && effect.remove_only_reference_from_one2many == true){
						changes[field].forEach((value, index) => {
							if (value[0] == 2){
								value[0] = 3
							}
						});
					}
				}
			}
			return changes;
		},
	});
});
