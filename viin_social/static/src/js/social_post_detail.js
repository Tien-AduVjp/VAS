odoo.define('viin_social.social_post_detail', function (require) {
"use strict";
var core = require('web.core');
var Dialog = require('web.Dialog');
var PostAttachmentsCarousel = require('viin_social.social_post_attachments_carousel');
var ViinSocialEmojisMixin = require('viin_social.emoji_mixin');
var emojis = require('mail.emojis');

var _t = core._t;
var QWeb = core.qweb;

var SocialPostDetail = Dialog.extend(ViinSocialEmojisMixin, {
	template: 'viin_social.SocialPostDetail',
	events: {
		'click .button_post_article': '_postArticle',
		'click .button_synchronized_post': '_synchronizePost',
		'click .post_image_attachment': '_showMoreAttachments',
		'click .button_reply_comment': '_showReplyInput',
		'click .button_like_comment': '_likeComment',
		'click .button_show_more_comment': '_showMoreComment',
		'click .button_show_more_reply': '_showReplyComment',
		'click .button_delete_comment': '_deleteComment',
		'click .comment_input .o_mail_emoji': '_onEmojiClick',
        'keydown .social_reply_comment_input textarea': '_replyComment',
        'keydown .social_write_comment_input textarea': '_addComment',
	},
	
	init: function(parent, options){
        this.options = _.defaults(options || {}, {
            title: options.title || _t('Social Post'),
            renderFooter: false,
            size: 'medium',
        });
		this.post_id = options.post_id;
        this.page_name = options.page_name;
        this.page_image = options.page_image;
        this.post_message = this._formatText(options.post_message);
        this.post_like_count = options.post_like_count;
        this.post_comment_count = options.post_comment_count;
        this.first_level_comment_count = options.first_level_comment_count;
        this.post_share_count = options.post_share_count;
        this.social_media_name = options.social_media_name;
        this.post_images = options.post_images;
		this.attachments = options.attachments;
		this.attachment_link = options.attachment_link;
		this.attachment_link_title = options.attachment_link_title;
        this.media = options.media;
        this.comments = this._formatCommentMessage(options.comments.slice(0,5));
		this.state = options.state;
		this.hide_comments = options.comments.slice(6,options.comments.length);
		this._super.apply(this, arguments);
		this.emojis = emojis;
	},

    /**
     * Post Article.
     *
     * @param {MouseEvent} ev
     */

    _postArticle: function (ev) {
        ev.preventDefault();
		this._rpc({
            model: 'social.post',
            method: 'action_post_article',
            args: [this.post_id],
		})
    },

    /**
     * Synchronize.
     *
     * @param {MouseEvent} ev
     */

    _synchronizePost: function (ev) {
        ev.preventDefault();
		var div_post_comment_count = $('.post_comment_count');
		var div_post_like_count = $('.post_like_count');
		var div_post_share_count = $('.post_share_count');
		this._rpc({
            model: 'social.post',
            method: 'update_post_engagement',
            args: [this.post_id],
		}).then(function(data){
			div_post_comment_count.text(data['comments_count']);
			div_post_like_count.text(data['likes_count']);
			div_post_share_count.text(data['shares_count']);
		});
    },

    /**
     * Show more post attachments.
     *
     * @param {MouseEvent} ev
     * @private
     */
    _showMoreAttachments: function (ev) {
        var $target = $(ev.currentTarget);
		var active_position = $target.attr('data-attachment-position');
        new PostAttachmentsCarousel(
            this, {
                'attachments': this.attachments,
				'active_position': active_position,
            }
        ).open();
    },

    /**
     * Show reply comment input.
     *
     * @param {MouseEvent} ev
     */

    _showReplyInput: function (ev) {
        ev.preventDefault();
        var $target = $(ev.currentTarget);
		var div_root_comment = $target.closest('.social_root_comment');
		var reply_content = div_root_comment.find('.social_reply_comment_input');
		var hide_div = div_root_comment.find('.d-none');
		hide_div.removeClass('d-none');
		reply_content.children("textarea").focus();
    },

    /**
     * Like a comment.
     *
     * @param {MouseEvent} ev
     */

    _likeComment: function (ev) {
        ev.preventDefault();
        var $target = $(ev.currentTarget);
		var current_comment = $target.closest('.social_comment');
		var div_like_count = current_comment.find('.comment_like_count').first();
		var social_comment_id = current_comment.attr("social_comment_id");
		this._rpc({
            model: 'social.post',
            method: 'like_comment',
            args: [this.post_id, social_comment_id],
		}).then(function(data){
			if (data){
				var new_like_count = parseInt(div_like_count.text()) + parseInt(data);
				div_like_count.text(new_like_count);
			}
		});
    },

    /**
     * Show more comment.
     *
     * @param {MouseEvent} ev
     */

    _showMoreComment: function (ev) {
        ev.preventDefault();
		if(this.hide_comments){
			var div_comment = $('.post_comments')
			var data = {comments: this._formatCommentMessage(this.hide_comments.slice(0,5)), page_image: this.page_image, emojis: this.emojis};
			this.hide_comments = this.hide_comments.slice(6,this.hide_comments.length);
			var comments = QWeb.render('viin_social.social_comment_template',{widget: data});
			div_comment.append(comments);
			if(this.hide_comments.length == 0){
				$('.button_show_more_comment').hide();
			}
		}
    },

    /**
     * Show reply comment.
     *
     * @param {MouseEvent} ev
     */

    _showReplyComment: function (ev) {
        ev.preventDefault();
        var self = this;
        var $target = $(ev.currentTarget);
		var div_root_comment = $target.closest('.social_root_comment');
		var div_reply_comments = div_root_comment.find('.reply_comments');
		var social_comment_id = div_root_comment.attr("social_comment_id")
		$target.hide();
		this._rpc({
            model: 'social.post',
            method: 'get_reply_comments',
            args: [this.post_id, social_comment_id],
		}).then(function(data){
			data.replys = self._formatCommentMessage(data.replys);
			var reply_comments = QWeb.render('viin_social.social_reply_template',{widget: data});
			div_reply_comments.append(reply_comments);
		});
    },

    /**
     * Reply a comment
     *
     * @param {MouseEvent} ev
     */

    _replyComment: function (ev) {
    	var self = this;
		if (ev.keyCode == 13 || ev.which == 13){
			if (!ev.shiftKey){
				ev.preventDefault();
				var $target = $(ev.currentTarget);
				var div_root_comment = $target.closest('.social_root_comment');
				var div_reply_comments = div_root_comment.find('.reply_comments');
				var social_comment_id = div_root_comment.attr("social_comment_id")
				var div_post_comment_count = $('.post_comment_count');
				var reply_message = $target.val()
				if (reply_message == ''){
					return;
				}
				$target.val('')
				this._rpc({
		            model: 'social.post',
		            method: 'add_comment',
		            args: [this.post_id, reply_message, social_comment_id],
				}).then(function(data){
					if (data) {
						data.replys = self._formatCommentMessage(data.replys);
						var reply_comments = QWeb.render('viin_social.social_reply_template',{widget: data});
						div_reply_comments.append(reply_comments);
						var new_comment_count = parseInt(div_post_comment_count.text()) + 1;
						div_post_comment_count.text(new_comment_count);
					}
				});
			}
		}
    },

    /**
     * Add a comment
     *
     * @param {MouseEvent} ev
     */

    _addComment: function (ev) {
    	var self = this;
		if (ev.keyCode == 13 || ev.which == 13){
			if (!ev.shiftKey){
				ev.preventDefault();
				var $target = $(ev.currentTarget);
				var comment_message = $target.val();
				if (comment_message == ''){
					return;
				}
				var div_write_comment = $target.closest('.modal_social_write_comment');
				var div_post_comment_count = $('.post_comment_count');
				var emojis = this.emojis;
				$target.val('')
				this._rpc({
		            model: 'social.post',
		            method: 'add_comment',
		            args: [this.post_id, comment_message],
				}).then(function(data){
					if(data) {
						data.emojis = emojis;
						data.comments = self._formatCommentMessage(data.comments);
						var comment = QWeb.render('viin_social.social_comment_template',{widget: data});
						div_write_comment.after(comment);
						var new_comment_count = parseInt(div_post_comment_count.text()) + 1;
						div_post_comment_count.text(new_comment_count);
					}
				});
			}
		}
    },


    /**
     * Delete a comment
     *
     * @param {MouseEvent} ev
     */

    _deleteComment: function (ev) {
        ev.preventDefault();
        var $target = $(ev.currentTarget);
		var current_comment = $target.closest('.social_comment');
		var social_comment_id = current_comment.attr("social_comment_id");
		var div_post_comment_count = $('.post_comment_count');
		this._rpc({
            model: 'social.post',
            method: 'delete_comment',
            args: [this.post_id, social_comment_id],
		}).then(function(data){
			if (data){
				current_comment.remove();
				var new_comment_count = parseInt(div_post_comment_count.text()) - 1;
				if (new_comment_count > 0){
					div_post_comment_count.text(new_comment_count);
				}
			}
		});
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Used by SocialEmojisMixin, check its document for more info.
     *
     * @param {$.Element} $emoji
     * @private
     */
    _getTargetTextArea($emoji) {
        return $emoji.closest('.comment_input').find('textarea');
    },

    /**
     * Format Comment message from Text to Html.
     */
    _formatCommentMessage(comments){
    	var self = this;
    	$.each(comments,function(){
    		this.message = self._formatText(this.message);
    	});
    	return comments;
    },


});

return SocialPostDetail;
});
