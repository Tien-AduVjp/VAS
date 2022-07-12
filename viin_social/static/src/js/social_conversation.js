odoo.define('viin_social.SocialConversation', function (require) {
"use strict";

var Discuss = require('mail.Discuss');
var core = require('web.core');

var QWeb = core.qweb;
var _t = core._t;

var SocialConversation = Discuss.extend({

    /**
     * @override
     * @param {Object} params
     * @param {Object} params.data
     */
    init: function (params) {
        this._super.apply(this, arguments);
		if (this.action.tag == 'viin_social.conversation') {
			this._social_page_id = this.context.default_page_id;
		}
    },

    /**
     * Overwrite the sidebar of discuss app
     *
     * @override
     * @private
     * @returns {jQueryElement}
     */
    _renderSidebar: function () {
		if (this.action.tag == 'viin_social.conversation') {
        var channels = this.call('mail_service', 'getChannels');
		channels = channels.filter(channel => channel._type == 'social_chat');
		if (this._social_page_id) {
			channels = channels.filter(channel => channel._social_page_id == this._social_page_id)
		}
;        channels = this._sortChannels(channels);
        var $sidebar = $(QWeb.render('viin_social.discuss.Sidebar', {
            activeThreadID: this._thread ? this._thread.getID() : undefined,
            moderation: this.call('mail_service', 'getMailbox', 'moderation'),
            channels: channels,
            isMyselfModerator: this.call('mail_service', 'isMyselfModerator'),
            displayQuickSearch: channels.length >= this.options.channelQuickSearchThreshold,
            options: this.options,
        }));
        return $sidebar;
		} else {
			return this._super.apply(this, arguments);
		}

    },

    /**
     * @override
     * @private
     * @param {Object} options
     * @param {string} [options.searchChannelVal='']
     */
    _renderSidebarChannels: function (options) {
		if (this.action.tag == 'viin_social.conversation') {
	        options.searchChannelVal = options.searchChannelVal || '';
	        var channels = this.call('mail_service', 'getChannels');
			channels = channels.filter(channel => channel._type == 'social_chat');
			if (this._social_page_id) {
				channels = channels.filter(channel => channel._social_page_id == this._social_page_id)
			}
	        channels = this._sortChannels(channels);
	        var searchChannelValLowerCase = options.searchChannelVal.toLowerCase();
	        channels = _.filter(channels, function (channel) {
	            var channelNameLowerCase = channel.getName().toLowerCase();
	            return channelNameLowerCase.indexOf(searchChannelValLowerCase) !== -1;
	        });
	        channels = this._sortChannels(channels);
	        this.$('.o_mail_discuss_sidebar_channels').html(
	            QWeb.render('viin_social.SocialConversation', {
	                activeThreadID: this._thread ? this._thread.getID() : undefined,
	                channels: channels,
	                displayQuickSearch: channels.length >= this.options.channelQuickSearchThreshold,
	            })
	        );
		} else {
			return this._super.apply(this, arguments);
		}
    },

});

core.action_registry.add('viin_social.conversation', SocialConversation);

return SocialConversation;

});
