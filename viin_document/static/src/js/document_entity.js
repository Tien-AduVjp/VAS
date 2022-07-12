odoo.define('viin_document.DocumentEntity', function (require) {
	"use strict";

	class DocumentEntity {

		constructor(doc_data) {
			this.doc_id = doc_data.doc_id;
			this.mimetype = doc_data.mimetype;
			this.display_name = doc_data.display_name;
			this.attachment_id = doc_data.attachment_id;
			this.workspace_id = doc_data.workspace_id;
			this.tag_ids = doc_data.tag_ids,
			this.action_ids = doc_data.action_ids,
			this.owner_id = doc_data.owner_id,
			this.url = doc_data.url,
			this.ytb_video_id = doc_data.ytb_video_id
		}

		isDocInSessionStorage() {
			let storage_documents = sessionStorage.getItem("session_storage_doc") !== null ? JSON.parse(sessionStorage.getItem("session_storage_doc")) : [];
			let self = this
			let exist_index = _.findIndex(storage_documents, function (doc) {
				return doc.doc_id == self.doc_id
			})
			return exist_index != -1 ? true : false
		}

		/**
		 *
		 * Update session storage when a document was selected or deselected.
		 */
		_updateSessionStorageSelectedDocuments({ action }) {
			let storage_documents = sessionStorage.getItem("session_storage_doc") !== null ? JSON.parse(sessionStorage.getItem("session_storage_doc")) : [];
			let self = this;
			switch (action) {
				case "add":
					storage_documents = [...storage_documents, self];
					break;
				case "remove":
					storage_documents = _.reject(storage_documents, function (d) {
						return d.doc_id === self.doc_id
					})
					break;
				case "reset":
					storage_documents = [self]
					break;
				case "clear":
					storage_documents = _.reject(storage_documents, function (d) {
						return d.doc_id !== self.doc_id
					})
					break;
			}
			sessionStorage.setItem('session_storage_doc', JSON.stringify(storage_documents))
		}

		static isDocInSessionStorage(doc_ids){
			let storage_documents = sessionStorage.getItem("session_storage_doc") !== null ? JSON.parse(sessionStorage.getItem("session_storage_doc")) : [];
			let exist_index = _.findIndex(storage_documents, function (doc) {
				return doc.doc_id == doc_ids
			})
			return exist_index != -1 ? true : false
		}
	}
	return DocumentEntity
})
