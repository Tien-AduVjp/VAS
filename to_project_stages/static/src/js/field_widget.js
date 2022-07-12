odoo.define('my_field_widget', function (require) {
"use strict";

	var AbstractField = require('web.AbstractField');
	var fieldRegistry = require('web.field_registry');
	var core = require('web.core');

	var qweb = core.qweb;

	var colorField = AbstractField.extend({
	    className: 'o_int_colorpicker',
	    tagName: 'span',
	    supportedFieldTypes: ['integer'],
	    events: {
	        'click .o_color_pill': 'clickPill',
	    },
	    init: function () {
	        this.totalColors = 12;
	        this._super.apply(this, arguments);
	    },
	    willStart: function () {
	        this.color_stage_name = {};
	        return this._super.apply(this, arguments);
	    },
	    _renderEdit: function () {
	        this.$el.empty();
	        for (var i = 0; i < this.totalColors; i++ ) {
	            var className = "o_color_pill o_color_" + i;
	            if (this.value === i ) {
	                className += ' active';
	            }
	            this.$el.append($('<span>', {
	                'class': className,
	                'data-val': i,
	            }));
	        }
	    },
	    _renderReadonly: function () {
	        this.$el.empty();
	        var pills = qweb.render('FieldColorPills', {widget: this});
	        this.$el.append(pills);
	    },
	    clickPill: function (ev) {
	        var $target = $(ev.currentTarget);
	        var data = $target.data();
		  if( data.val != null)
	        	this._setValue(data.val.toString());
	    }

	});

	fieldRegistry.add('int_color', colorField);

	return {
	    colorField: colorField,
	};
}); 
