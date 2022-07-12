odoo.define('to_account_reports.ActionManager', function (require) {
"use strict";

var session = require('web.session');
var ActManager = require('web.ActionManager');
var fw = require('web.framework');

ActManager.include({
    _handleAction: function (action, options) {
        if (action.type === 'ir_actions_af_report_dl') {
            return this._executeARDAction(action, options);
        }
        return this._super.apply(this, arguments);
    },
	_executeARDAction: function (action) {
        var self = this;
        fw.blockUI();
        return new Promise(function (resolve, reject) {
            session.get_file({
                url: '/to_account_reports',
                data: action.data,
                success: resolve,
                error: (error) => {
                    self.call('crash_manager', 'rpc_error', error);
                    reject();
                },
                complete: fw.unblockUI,
            });
        });
    },
});

});
