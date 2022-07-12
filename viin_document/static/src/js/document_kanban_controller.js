odoo.define('viin_document.DocumentKanbanController', function (require) {
	"use strict";

	/**
	 * Refer to mrp module of Odoo CE
	 * https://github.com/odoo/odoo/blob/14.0/addons/mrp/static/src/js/mrp_documents_kanban_controller.js
	 */

	const DocumentEntity = require('viin_document.DocumentEntity');
	const KanbanController = require('web.KanbanController');
	const DocumentControllerMixin = require('viin_document.controllerMixin');

	const DocumentKanbanController = KanbanController.extend(DocumentControllerMixin, {
		events: Object.assign({}, KanbanController.prototype.events, DocumentControllerMixin.events),
		custom_events: Object.assign({}, KanbanController.prototype.custom_events, DocumentControllerMixin.custom_events, {
			selected_single_record: '_onSelectedSingleDocument',
			selected_multiple_record: '_onSelectedMultipleDocument',
			records_checked: '_onRecordChecked'
		}),
		/**
		 * @override
		 */
		init() {
			this._super(...arguments);
			DocumentControllerMixin.init.apply(this, arguments);
			this.records_checked = [],
				this.select_mode = 'none'
		},

		_onRecordChecked: function (ev) {
			this.records_checked = [...this.records_checked, ev.data.record_checked]
			this.select_mode = this.records_checked.length > 1 ? 'multiple' : 'single'
		},

		_onSelectedSingleDocument: function (ev) {
			let doc = new DocumentEntity(ev.data.doc_data)
			let record_checked = ev.data.record_checked
			doc._updateSessionStorageSelectedDocuments({ action: "clear" })
			$('.o_kanban_record').not(ev.target.$el).removeClass('border-success')
			_.forEach(this.records_checked, function (rec) {
				if (rec.documentId !== record_checked.documentId) {
					rec.unCheckRecord()
				}
			})
			if (doc.isDocInSessionStorage()) {
				if (this.select_mode != 'multiple') {
					ev.target.$el.removeClass("border-success")
					record_checked.unCheckRecord()
					this.records_checked = _.reject(this.records_checked, function (rec) {
						return rec.documentId === record_checked.documentId
					})
					doc._updateSessionStorageSelectedDocuments({ action: "remove" })
				}
			} else {
				ev.target.$el.addClass("border-success")
				record_checked.checkRecord()
				this.records_checked = [ev.data.record_checked]
				doc._updateSessionStorageSelectedDocuments({ action: "reset" })
			}
			this.sidebar_widget.updatePreviewDocuments()
			this.select_mode = 'single'
			this._toggleSidebar(doc.isDocInSessionStorage());
		},

		_onSelectedMultipleDocument: function (ev) {
			let record_checked = ev.data.record_checked
			let doc = new DocumentEntity(ev.data.doc_data)
			if (doc.isDocInSessionStorage()) {
				ev.target.$el.removeClass("border-success")
				record_checked.unCheckRecord()
				this.records_checked = _.reject(this.records_checked, function (rec) {
					return rec.documentId === record_checked.documentId
				})
				doc._updateSessionStorageSelectedDocuments({ action: "remove" })
			} else {
				ev.target.$el.addClass("border-success")
				record_checked.checkRecord()
				this.records_checked = [...this.records_checked, ev.data.record_checked]
				doc._updateSessionStorageSelectedDocuments({ action: "add" })
			}
			this.sidebar_widget.updatePreviewDocuments()
			this.select_mode = 'multiple'
			this._toggleSidebar(!!JSON.parse(sessionStorage.getItem("session_storage_doc")).length);
		},

		async reload() {
			await this._super(...arguments);
			await DocumentControllerMixin.reload.call(this, ...arguments);
		},


	});

	return DocumentKanbanController;
})
