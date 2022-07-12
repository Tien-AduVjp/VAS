odoo.define('viin_social.form_field_post_preview', function (require) {
"use strict";

var FieldHtml = require('web_editor.field.html');
var fieldRegistry = require('web.field_registry');
var ViinSocialEmojisMixin = require('viin_social.emoji_mixin');

var FieldPostPreview = FieldHtml.extend(ViinSocialEmojisMixin, {
    _textToHtml: function (text) {
        var html = this._super.apply(this, arguments);
        var $html = $(html);
        var $previewMessage = $html.find('.viin_social_preview_message');
        $previewMessage.html(this._formatText($previewMessage.text().trim()));

        return $html[0].outerHTML;
    }
});

fieldRegistry.add('viin_social_post_preview', FieldPostPreview);

return FieldPostPreview;

});
