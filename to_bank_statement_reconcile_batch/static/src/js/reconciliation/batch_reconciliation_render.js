odoo.define('to_bank_statement_reconcile_batch.BatchReconcilliationRender', function (require) {
"use strict";

	var ReconciliationRenderer = require('account.ReconciliationRenderer');
	
	ReconciliationRenderer.LineRenderer.include({
		update: function (state) {
			var defs = this._super.apply(this, arguments);
			this.trigger_up('show_batch_reconcile');
			return defs
		},
		});
});