odoo.define('viin_social.mail.Manager', function(require) {
	'use strict';

	var MailManager = require('mail.Manager');
	var SocialChat = require('viin_social.model.SocialChat');

	MailManager.include({
	    _makeChannel: function (data, options) {
	        if (data.channel_type === 'social_chat') {
	            return new SocialChat({
	                parent: this,
	                data: data,
	                options: options,
	                commands: this._commands,
	            });
	        } else {
				return this._super.apply(this, arguments);
			}
	    },

	});
});