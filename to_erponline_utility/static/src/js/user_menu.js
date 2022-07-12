odoo.define('to_erponline_utility.UserMenu', function(require) {
	"use strict";
	var UserMenu = require('web.UserMenu');
	UserMenu.include({
		_onMenuDocumentation: function() {
			window.open('https://erponline.vn/vi/docs/13.0', '_blank');
		},

		_onMenuSupport: function() {
			window.open('https://viindoo.com/ticket', '_blank');
		},
	});
	return UserMenu;
});