odoo.define('viin_social.update_kanban', function(require) {
	'use strict';

	var KanbanRecord = require('web.KanbanRecord');
	var SocialPostDetail = require('viin_social.social_post_detail');

	KanbanRecord.include({
		_openRecord : function() {
			if (this.modelName === 'social.post') {
				this._getPostdetail();
			} else {
				this._super.apply(this, arguments);
			}
		},

	_getPostdetail : function() {
		var self = this;
        this._rpc({
            model: 'social.post',
            method: 'get_post_content',
            args: [this.id],
       
        }).then(function (data){
		new SocialPostDetail(self,{
			post_id: data.post_id,
            page_name: data.page_name,
            page_image: data.page_image,
            post_message: data.post_message,
            post_like_count : data.post_like_count,
            post_comment_count : data.post_comment_count,
			first_level_comment_count:data.first_level_comment_count,
            post_share_count : data.post_share_count,
            social_media_name : data.social_media_name,
            post_images: data.post_images,
            attachments: data.attachments,
			attachment_link: data.attachment_link,
            attachment_link_title: data.attachment_link_title,
            media: data.media,
            comments: data.comments,
			state: data.state,
		}).open();
		});
	},

	});
});
