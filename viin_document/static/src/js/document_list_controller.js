odoo.define('viin_document.DocumentListController', function (require) {
	"use strict";

	/**
	 * Refer to mrp module of Odoo CE
	 * https://github.com/odoo/odoo/blob/14.0/addons/mrp/static/src/js/mrp_documents_kanban_controller.js
	 */

	const ListController = require('web.ListController');
	const DocumentControllerMixin = require('viin_document.controllerMixin');
	const DocumentEntity = require('viin_document.DocumentEntity');

	const DocumentListController = ListController.extend(DocumentControllerMixin, {
		events: Object.assign({}, ListController.prototype.events, DocumentControllerMixin.events),
		custom_events: Object.assign({}, ListController.prototype.custom_events, DocumentControllerMixin.custom_events, {
			selected_record: '_onSelectRecord',
			selected_all_record: '_onSelectedAllRecord',
			unselected_all_record: '_onUnSelectedAllRecord'
		}),
		init() {
			this._super(...arguments);
			DocumentControllerMixin.init.apply(this, arguments);
		},

		/**
		 *
		 * @override
		 */
		_onDeletedRecords(ids) {
			this._super.apply(this, arguments)
			sessionStorage.setItem('session_storage_doc', JSON.stringify([]));
			this.sidebar_widget.updatePreviewDocuments()
		},

		_onSelectRecord(ev) {
			let self = this
			this._rpc({
				route: '/document/read',
				params: {
					document_ids: ev.data.documentId,
					fields: ['id', 'name', 'mimetype', 'attachment_id', 'workspace_id', 'tag_ids', 'owner_id']
				},
			}).then(function (res) {
				res.forEach(element => {
					let doc = new DocumentEntity(element)
					if (doc.isDocInSessionStorage()) {
						doc._updateSessionStorageSelectedDocuments({ action: "remove" })
					} else {
						doc._updateSessionStorageSelectedDocuments({ action: "add" })
					}
					self.sidebar_widget.updatePreviewDocuments()
				});
			});
		},

		_onSelectedAllRecord(ev) {
			let self = this
			this._rpc({
				route: '/document/read',
				params: {
					document_ids: ev.data.document_ids,
					fields: ['id', 'name', 'mimetype', 'attachment_id', 'workspace_id', 'tag_ids','owner_id']
				},
			}).then(function (res) {
				let storage_documents = []
				res.forEach(element => {
					let doc = new DocumentEntity(element)
					storage_documents = [...storage_documents, doc]
				});
				sessionStorage.setItem('session_storage_doc', JSON.stringify(storage_documents))
				self.sidebar_widget.updatePreviewDocuments()
			});
		},

		_onUnSelectedAllRecord() {
			sessionStorage.setItem('session_storage_doc', JSON.stringify([]))
			this.sidebar_widget.updatePreviewDocuments()
		},

		async reload() {
			await this._super(...arguments);
			await DocumentControllerMixin.reload.call(this, ...arguments);
		},
	});

	return DocumentListController;
})
