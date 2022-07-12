odoo.define('viin_social.social_notice_read_all_notice', function (require) {
"use strict";
var core = require('web.core');
var ListController = require('web.ListController');
var rpc = require('web.rpc');
var session = require('web.session');
var _t = core._t;

var includeDict = {
   renderButtons: function($node) {
   this._super.apply(this, arguments);
       if (this.$buttons) {
         this.$buttons.find('.action-read-all-notice').click(this.proxy('action_read_all_notices')) ;
       }
   	},
	action_read_all_notices: function () {
            var self =this
            var user = session.uid;
            rpc.query({
                model: 'social.notice',
                method: 'action_read_all_notices',
                args: [[user]],
                }).then(function(){
				self.reload();
				});
            },
	};
ListController.include(includeDict)
});
