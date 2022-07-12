odoo.define('viin_social.model.SocialChat', function (require) {
"use strict";

var TwoUserChannel = require('mail.model.TwoUserChannel');

/**
 * backend-side of the social_chat.
 *
 */
var SocialChat = TwoUserChannel.extend({

    /**
     * @override
     * @param {Object} params
     * @param {Object} params.data
     */
    init: function (params) {
        this._super.apply(this, arguments);
        this._type = 'social_chat';
		this._social_page_id = params.data.social_page_id;
    },

});

return SocialChat;

});
