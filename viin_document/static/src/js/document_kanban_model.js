odoo.define('viin_document.DocumentKanbanModel', function (require) {
    "use strict";

    const KanbanModel = require('web.KanbanModel');
    const DocumentModel = require('viin_document.DocumentModel');
    const DocumentKanbanModel = KanbanModel.extend(DocumentModel, {})

    return DocumentKanbanModel;
})
