odoo.define('viin_document.DocumentDocumentViewer', function(require){
    "use strict";

    const DocumentViewer = require('mail.DocumentViewer')

    const DocumentDocumentViewer = DocumentViewer.extend({
        init(parent, attachments, activeAttachmentID) {
            this._super(...arguments);
            this.modelName = 'document.document';
        },
    })

    return DocumentDocumentViewer
})
