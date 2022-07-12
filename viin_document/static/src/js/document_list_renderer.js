odoo.define('viin_document.DocumentListRenderer', function (require) {
    "use strict";
    /**
     * This file defines the Renderer for the Document List view, which is an
     * override of the ListRenderer.
     */

    const ListRenderer = require('web.ListRenderer');
    const DocumentEntity = require('viin_document.DocumentEntity');


    const DocumentListRenderer = ListRenderer.extend({

        /**
         * @override
         */
        start: function () {
            this.$el.addClass('v_document_view');
            return this._super.apply(this, arguments);
        },

        /**
         * Override to add id of document in dataset.
         *
         * @override
         */
        _renderRow: function (record) {
            let tr = this._super.apply(this, arguments);
            tr.attr('data-document-id', record.data.id);
            if (DocumentEntity.isDocInSessionStorage(record.data.id)) {
                var ev = $.Event();
                ev.target = tr.find('.custom-control.custom-checkbox')
                this._onToggleCheckbox(ev)
            }
            return tr;
        },

        /**
         * @override
         */
        _onSelectRecord(ev) {
            this._super.apply(this, arguments);
            let documentId = $(ev.currentTarget.closest('tr.o_data_row')).data('document-id')
            this.trigger_up('selected_record', { documentId: [documentId] })
        },

        /**
         * @override
         */
        _onToggleSelection(ev) {
            this._super.apply(this, arguments);
            let checked = $(ev.currentTarget).prop('checked') || false;
            if (checked) {
                let document_ids = []
                this.$('tbody .o_list_record_selector input:not(":disabled")').map(function () {
                    document_ids = [...document_ids, $(this).closest('tr.o_data_row').data('document-id')]
                });
                this.trigger_up('selected_all_record', { document_ids })
            } else {
                this.trigger_up('unselected_all_record')
            }
        }

    })
    return DocumentListRenderer
})
