odoo.define('viin_message_emoji.MailManager', function (require){
    "use strict";
        
    var MailManager = require('mail.Manager');
    MailManager.include({
        _handleChannelNotification: function (params) {
            if (params.data && params.data.info === 'increate_emoji') {
                this._handleChannelUpdateEmojiNotification(params.channelID, params.data);
            } else {
                this._super.apply(this, arguments);
            }
        },

        _handleChannelUpdateEmojiNotification: function (channelID, data) {
            var self = this;
            const {emoji_up, emoji_down, message_id} = data;
            var message = _.find(self._messages, function (msg) {
                return msg.getID() === message_id;
            });
            if(message!=undefined){
                const thread = this.call('mail_service', 'getThread', channelID);
                thread.updateCacheEmoji({message_id, emoji_up, emoji_down});
                self._mailBus.trigger('update_message', message);
            }
        },
    });
    return MailManager;
})
