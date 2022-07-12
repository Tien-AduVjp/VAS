odoo.define('social_chat/static/src/models/messaging_initializer/messaging_initializer.js', function (require) {
'use strict';

const { registerInstancePatchModel } = require('mail/static/src/model/model_core.js');
const { executeGracefully } = require('mail/static/src/utils/utils.js');

registerInstancePatchModel('mail.messaging_initializer', 'social_chat/static/src/models/messaging_initializer/messaging_initializer.js', {

    //----------------------------------------------------------------------
    // Private
    //----------------------------------------------------------------------

    /**
     * @override
     * @param {Object[]} [param0.channel_social_chat=[]]
     */
    async _initChannels(initMessagingData) {
        await this.async(() => this._super(initMessagingData));
        const { channel_social_chat = [] } = initMessagingData;
        return executeGracefully(channel_social_chat.map(data => () => {
            const channel = this.env.models['mail.thread'].insert(
                this.env.models['mail.thread'].convertData(data),
            );

            if (!channel.isPinned) {
                channel.pin();
            }
        }));
    },
});

});
