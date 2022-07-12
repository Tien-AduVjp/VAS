odoo.define('to_bank_statement_reconcile_batch.BatchReconcilliationAction', function (require) {
"use strict";

	var ReconciliationClientAction = require('account.ReconciliationClientAction');

	ReconciliationClientAction.StatementAction.include({
		events: {
			'click .batch_reconcile': '_doBatchReconcile',
		},
		
		custom_events: _.extend({},ReconciliationClientAction.StatementAction.prototype.custom_events,{
			show_batch_reconcile:'_onBatchReconcile'	
		}),
		
		_doBatchReconcile: function() {
			$(".o_reconcile:not('.d-none')").click();
	    },
	    
	    _openFirstLine: function (previous_handle) {
	    	var defs = this._super.apply(this, arguments);
			this._onBatchReconcile()
			return defs
	    },
	    
	    _onBatchReconcile: function() {
			var x = this.$(".o_reconcile:not('.d-none')");
			if(x.length == 0){this.$('.batch_reconcile').prop('disabled', true).removeClass('btn-primary').addClass('btn-secondary')}
			else{this.$('.batch_reconcile').prop('disabled', false).removeClass('btn-secondary').addClass('btn-primary')}
	
	    }
	});

});
