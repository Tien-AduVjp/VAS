odoo.define('viin_website_livechat.livechat_request', function(require) {
	"use strict";

	var utils = require('web.utils');
	var session = require('web.session');
	var LivechatButton = require('im_livechat.im_livechat').LivechatButton;


	LivechatButton.include({

		/**
		 * @override
		 * add channel based on visitor_uuid
		 */
		start: function() {
			this._super();
			this.call('bus_service', 'addChannel', utils.get_cookie('visitor_uuid'));
			this.call('bus_service', 'startPolling');
		},

		_openlivechatImmediate: function(notification) {
			self = this;
			var channel = notification[0];
			var cookie_info = notification[1];
			if (channel === utils.get_cookie('visitor_uuid')) {
				this._messages = [];
				utils.set_cookie('im_livechat_session', utils.unaccent(JSON.stringify(cookie_info)), 60 * 60 * 24);
				this.willStart().then(function() {
					if (self._history) {
						_.each(self._history.reverse(), self._addMessage.bind(self));
						if (!self._chatWindow){
                            self._openChat();
                        }
							
					}
				});
			};

		},

		_onNotification: function(notifications) {
			var self = this;
			_.each(notifications, function(notification) {
				self._openlivechatImmediate(notification);
			});
			this._super(notifications);
		},
	});

	return {
		LivechatButton: LivechatButton,
	};

});
