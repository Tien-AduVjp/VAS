odoo.define('to_erponline_utility.UserMenu', function(require) {
	"use strict";
	var UserMenu = require('web.UserMenu');
	UserMenu.include({

		_onMenuAccount: function(){
			window.open('https://viindoo.com', '_blank');
		},

		_onMenuDocumentation: function() {
			window.open('https://viindoo.com/documentation/14.0/', '_blank');
		},

		_onMenuSupport: function() {
			window.open('https://viindoo.com/ticket', '_blank');
		},
	});
	return UserMenu;
});
