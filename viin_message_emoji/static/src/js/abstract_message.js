odoo.define('viin_message_emoji.AbstractMessage', function (require){
    "use strict";
        
    var AbstractMessage = require('mail.model.AbstractMessage');
    AbstractMessage.include({
        init: function (parent, data) {
            this._super.apply(this, arguments);
            this.model = data.model;
            this.emoji = data.emoji;
            this.listEmoji = data.list_emoji;
        },
    });
    return AbstractMessage;
})
