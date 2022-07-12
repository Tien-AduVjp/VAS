odoo.define('to_fleet_vehicle_revenue_accounting.widget', function(require) {
	"use strict";

	var AbstractField = require('web.AbstractField');
	var core = require('web.core');
	var registry = require('web.field_registry');

	var _t = core._t;

	var WidgetBusRevButton = AbstractField.extend({
		events: _.extend({}, AbstractField.prototype.events, {
	        'click': '_onClick',
	    }),
	    description: "",
	    
	    //--------------------------------------------------------------------------
	    // Private
	    //--------------------------------------------------------------------------

	    /**
	     * @override
	     * @private
	     */
	    _render: function () {
	        var className = '';
	        var title;
	        if (this.recordData.has_vehicle_revenue) {
	            className = 'o_has_vehicle_revenue';
	            title = _t('Distributed into Vehicle Revenues');
	        } else {
	            className = 'o_no_vehicle_revenue';
	            title = _t('Not distributed into vehicle revenues yet');
	        }
	        var $button = $('<button/>', {
	            type: 'button',
	            title: title,
	        }).addClass('btn btn-sm btn-link fa fa-bus o_widgetbusrevbutton ' + className);
	        this.$el.html($button);
	    },
	    
		//--------------------------------------------------------------------------
	    // Handlers
	    //--------------------------------------------------------------------------

	    /**
	     * @private
	     * @param {MouseEvent} event
	     */
	    _onClick: function (event) {
	        event.stopPropagation();
	        this.trigger_up('button_clicked', {
	            attrs: {
	                name: 'action_vehicle_revenue_allocation_wizard',
	                type: 'object',
	            },
	            record: this.record,
	        });
	    },
	    
	});

	registry.add("widgetbusrevbutton", WidgetBusRevButton);
	return WidgetBusRevButton;

	});
