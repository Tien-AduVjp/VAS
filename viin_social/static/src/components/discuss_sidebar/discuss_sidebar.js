odoo.define('viin_social/static/src/components/discuss_sidebar/discuss_sidebar.js', function (require) {
'use strict';

const components = {
    DiscussSidebar: require('mail/static/src/components/discuss_sidebar/discuss_sidebar.js'),
};

const { patch } = require('web.utils');

patch(components.DiscussSidebar, 'viin_social/static/src/components/discuss_sidebar/discuss_sidebar.js', {

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Return the list of social chat that match the quick search value input.
     *
     * @returns {mail.thread[]}
     */
    quickSearchOrderedAndPinnedSocialChatList() {
        const all_social_chat = this.env.models['mail.thread']
            .all(thread =>
                thread.channel_type == 'social_chat' &&
                thread.isPinned &&
                thread.model === 'mail.channel'
            )
        if (!this.discuss.sidebarQuickSearchValue) {
            return all_social_chat;
        }
        const qsVal = this.discuss.sidebarQuickSearchValue.toLowerCase();
        return all_social_chat.filter(socialChat => {
            const nameVal = socialChat.displayName.toLowerCase();
            return nameVal.includes(qsVal);
        });
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _useStoreCompareDepth() {
        return Object.assign(this._super(...arguments), {
            all_social_chat: 1,
        });
    },
    /**
     * Override to include social chat channels on the sidebar.
     *
     * @override
     */
    _useStoreSelector(props) {
        return Object.assign(this._super(...arguments), {
            all_social_chat: this.quickSearchOrderedAndPinnedSocialChatList(),
        });
    },

});

});
