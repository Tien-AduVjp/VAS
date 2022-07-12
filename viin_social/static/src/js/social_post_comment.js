odoo.define('viin_social.update_kanban', function(require) {
'use strict';

var KanbanRecord = require('web.KanbanRecord');
var SocialPostDetail = require('viin_social.social_post_detail');

KanbanRecord.include({
	_openRecord: function() {
		var self = this;
		if (this.modelName === 'social.post') {
			Promise.all([this._getPostDetailData(), this._getPostEngagementData()]).then(values => {
				var socialPostDetail = new SocialPostDetail(self, {
					post_id: values[0].post_id,
					page_name: values[0].page_name,
					page_image: values[0].page_image,
					post_message: values[0].post_message,
					post_like_count: values[0].post_like_count,
					post_comment_count: values[0].post_comment_count,
					first_level_comment_count: values[0].first_level_comment_count,
					post_share_count: values[0].post_share_count,
					social_media_name: values[0].social_media_name,
					post_images: values[0].post_images,
					attachments: values[0].attachments,
					attachment_link: values[0].attachment_link,
					attachment_link_title: values[0].attachment_link_title,
					media: values[0].media,
					comments: values[0].comments,
					state: values[0].state,
					post_engagement: values[1]
				});
				socialPostDetail.open().opened().then(v => socialPostDetail.synchronizePost());
			});
		} else {
			this._super.apply(this, arguments);
		}
	},

	_getPostDetailData: async function() {
		return await this._rpc({
			model: 'social.post',
			method: 'get_post_content',
			args: [this.id],
		})
	},

	_getPostEngagementData: async function() {
		return await this._rpc({
			model: 'social.post',
			method: 'update_post_engagement',
			args: [this.id],
		})
	},


});
});
