odoo.define('viin_mobile/static/description/src/components/chat_window_manager/chat_window_manager.js', function (require) {

    'use strict';
    const components = {
        ChatWindowManager: require('mail/static/src/components/chat_window_manager/chat_window_manager.js'),
    };
    const { patch } = require('web.utils');

    patch(components.ChatWindowManager, 'viin_mobile/static/description/src/components/chat_window_manager/chat_window_manager.js', {

        /**
        * @override
        */
        isExpandable() {
            if (this.chatWindow.thread && this.chatWindow.thread.model == 'mail.channel' && this.env.messaging.device.isMobile) {
                return false;
            }
            return true;
        },
    })
});
