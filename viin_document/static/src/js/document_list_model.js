odoo.define('viin_document.DocumentListModel', function (require) {
    "use strict";

    const ListModel = require('web.ListModel');
    const DocumentModel = require('viin_document.DocumentModel');
    const DocumentListModel = ListModel.extend(DocumentModel, {})
    return DocumentListModel;
})
