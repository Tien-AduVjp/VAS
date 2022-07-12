odoo.define('viin_document.DocumentKanbanRecord', function (require) {
    "use strict";
    const KanbanRecord = require('web.KanbanRecord');
    const DocumentEntity = require('viin_document.DocumentEntity')
    const { Component, useState } = owl;
    const { xml } = owl.tags;
    class KanbanRecordChecked extends Component {
        constructor() {
            super(...arguments);
            this.state = useState({
                isSelected: false
            })
        }
        toggleSelectDocument(ev) {
            ev.stopPropagation()
            $(ev.target).parents('.o_kanban_record').trigger('multiple_select')
        }
        setDocumentId(doc_id) {
            this.documentId = doc_id
        }
        checkRecord() {
            this.state.isSelected = true
        }
        unCheckRecord() {
            this.state.isSelected = false
        }
    };
    /**
     * Multiple select records
     */
    Object.assign(KanbanRecordChecked, {
        template: xml`
            <span t-on-click="toggleSelectDocument">
                <b t-if = "state.isSelected==false" class="fa fa-circle-thin"/>
                <b t-else="true" class="fa fa-check-circle text-success"/>
            </span>`
    });

    const DocumentKanbanRecord = KanbanRecord.extend({

        events: _.extend({}, KanbanRecord.prototype.events, {
            'click': '_onSelectDocumentRecord',
            'multiple_select': '_onMultipleSelect',
            'click .o_kanban_previewer': '_onImageClicked'
        }),

        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments)
            this.KanbanRecordChecked = new KanbanRecordChecked();
            this.recordDoc = new DocumentEntity({
                doc_id: this.recordData.id,
                mimetype: this.recordData.mimetype,
                display_name: this.recordData.name,
                attachment_id: this.recordData.attachment_id.data,
                workspace_id: this.recordData.workspace_id.data,
                tag_ids: this.recordData.tag_ids.data.map( t => { return t.data } ),
                owner_id: this.recordData.owner_id.data
            })
        },

        /**
         * @override
         */
        start: function () {
            this._super.apply(this, arguments)
            this.KanbanRecordChecked.setDocumentId($(this.el).data('document-id'))
            this.KanbanRecordChecked.mount(this.el.querySelector('.v_document_kanban_record_checked'));
            if (this.recordDoc.isDocInSessionStorage()) {
                $(this.el).addClass('border-success')
                this.KanbanRecordChecked.checkRecord()
                this.trigger_up('records_checked', { record_checked: this.KanbanRecordChecked })
            }
        },

        /**
         * Add to the list selected documents
         *
         * @private
         * @param {MouseEvent} ev Click event
         */
        _onSelectDocumentRecord: function (ev) {
            ev.preventDefault();
            let doc_data = {
                doc_id: this.recordData.id,
                mimetype: this.recordData.mimetype,
                display_name: this.recordData.name,
                attachment_id: this.recordData.attachment_id.data,
                workspace_id: this.recordData.workspace_id.data,
                tag_ids: this.recordData.tag_ids.data.map(t => { return t.data }),
                action_ids: this.recordData.action_ids.data.map(a => { return a.data }),
                owner_id: this.recordData.owner_id.data,
                url: this.recordData.url,
                ytb_video_id: this.recordData.ytb_video_id
            }
           this.trigger_up('selected_single_record', { doc_data, record_checked: this.KanbanRecordChecked });
        },

        /**
        * @private
        * Selected multiple documents
        */
        _onMultipleSelect: function (ev) {
            ev.preventDefault()
            let doc_data = {
                doc_id: this.recordData.id,
                mimetype: this.recordData.mimetype,
                display_name: this.recordData.name,
                attachment_id: this.recordData.attachment_id.data,
                workspace_id: this.recordData.workspace_id.data,
                tag_ids: this.recordData.tag_ids.data.map( t => { return t.data } ),
                action_ids: this.recordData.action_ids.data.map(a => { return a.data }),
                owner_id: this.recordData.owner_id.data,
                url: this.recordData.url,
                ytb_video_id: this.recordData.ytb_video_id
            }
            this.trigger_up('selected_multiple_record', { doc_data, record_checked: this.KanbanRecordChecked });
        },

        /**
         * @private
         * @reference
		 * Copyright Odoo CE (mrp)
		 * https://github.com/odoo/odoo/blob/14.0/addons/mrp/static/src/js/mrp_documents_kanban_record.js#L38-L45
		 */
        _onImageClicked: function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            console.log(this.recordData)
            this.trigger_up('kanban_image_clicked', {
                recordList: [this.recordData],
                recordID: this.recordData.id
            });
        }
    })

    return DocumentKanbanRecord
})
