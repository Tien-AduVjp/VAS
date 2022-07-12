odoo.define('viin_social.social_post_attachments_carousel', function (require) {
"use strict";

var core = require('web.core');
var Dialog = require('web.Dialog');
var _t = core._t;

var PostAttachmentsCarousel = Dialog.extend({
    template: 'viin_social.PostAttachmentsCarousel',

    init: function (parent, options) {
        options = _.defaults(options || {}, {
            title: _t('Post Attachments'),
            renderFooter: false
        });
        this.attachments = options.attachments;
        if (options.active_position){
        	this.active_position = options.active_position;
        }
        else{
        	this.active_position = 0;
        }

        this._super.apply(this, arguments);
    }
});

return PostAttachmentsCarousel;

});
