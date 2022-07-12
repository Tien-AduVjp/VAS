odoo.define('viin_message_emoji.ThreadWidget', function (require){
    "use strict";
        
    var ThreadWidget = require('mail.widget.Thread');
    ThreadWidget.include({
        events: _.extend({}, ThreadWidget.prototype.events, {
            'click .click_emoji': '_onClickEmoji',
        }),
        _onClickEmoji: function (ev) {
            var messageID = $(ev.currentTarget).data('message-id');
            var emojiName = $(ev.currentTarget).data('emoj-name');
            this._rpc({
                route:'/message/increate/emoji',
                params: {message_id: messageID, emoji_name: emojiName},
            })
        },
    });
    return ThreadWidget;
})
