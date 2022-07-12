odoo.define('viin_document.DocumentKanbanRenderer', function (require) {
    "use strict";

    const KanbanRenderer = require('web.KanbanRenderer');
    const DocumentKanbanRecord = require('viin_document.DocumentKanbanRecord');
    const DocumentKanbanRenderer = KanbanRenderer.extend({
        config: _.extend({}, KanbanRenderer.prototype.config, {
            KanbanRecord: DocumentKanbanRecord
        }),
        /**
         * @override
         */
        start: function () {
            this.$el.addClass('v_document_view')
            return this._super.apply(this, arguments)
        },
    })
    return DocumentKanbanRenderer
})
