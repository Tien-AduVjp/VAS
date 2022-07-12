odoo.define('viin_social.social_post_button_synchronize', function(require) {
	"use strict";
	var ListController = require('web.ListController');
	var rpc = require('web.rpc');
	var session = require('web.session');

	var includeDict = {
		renderButtons: function() {
			this._super.apply(this, arguments);
			if (this.$buttons) {
				this.$buttons.on('click', '.action-synchronize-all-posts', do_action);
				};
			},
	};
	var do_action = function() {
		var user = session.uid;
		rpc.query({
		model: 'social.post',
		method: 'action_synchronize_all_post',
		args: [[user]],
		});
	};
	ListController.include(includeDict);
});
