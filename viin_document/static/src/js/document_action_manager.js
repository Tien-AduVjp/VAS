odoo.define('viin_document.action_manager', function (require) {
    'use strict';

    var ActionManager = require('web.ActionManager');

    ActionManager.include({
        _executeCloseAction: function (action, options) {
            if (action.effect && action.effect.keep_dialog_open) {
                var result = options.on_close(action.infos);
                return Promise.resolve(result);
            } else {
                return this._super.apply(this, arguments);
            }
        }
    })
})
