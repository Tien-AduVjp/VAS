odoo.define('to.attachment_preview', function (require) {
"use strict";

var relational_fields = require('web.relational_fields');
var fieldRegistry = require('web.field_registry');
var DocumentViewer = require('mail.DocumentViewer');

var FieldMany2ManyBinaryMultiFiles = relational_fields.FieldMany2ManyBinaryMultiFiles;

var FieldMany2ManyBinaryMultiFilesPreview = FieldMany2ManyBinaryMultiFiles.extend({
    events: _.extend({}, FieldMany2ManyBinaryMultiFiles.prototype.events, {
        'click a[title]': '_onClickAttachment'
    }),

	init: function () {
        this._super.apply(this, arguments);
		this.value.data.reverse();
	},

    _prepareDataForViewer: function() {
        this.attachments = _.map(this.value.data, function (iter) {
            var data = iter.data;
            var mimetype = data.mimetype
            if (mimetype === 'application/octet-stream') {
                mimetype = 'image/png'
            }
            return {
                'id': data.id,
                'mimetype': mimetype,
                'name': data.name,
                'url': '/web/content/' + data.id + '?download=true'
            };
        });
    },

    _render: function() {
        this._prepareDataForViewer();
        this._super.apply(this, arguments);
    },

    _onClickAttachment: function(event) {
        var activeAttachmentID = $(event.currentTarget).data('id');
        if (activeAttachmentID) {
            var attachmentViewer = new DocumentViewer(this, this.attachments, activeAttachmentID);
            attachmentViewer.appendTo($('body'));
        }
        return false;
    }
});

fieldRegistry.add('many2many_binary_preview', FieldMany2ManyBinaryMultiFilesPreview);

return FieldMany2ManyBinaryMultiFilesPreview;
});
