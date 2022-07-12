document.addEventListener("DOMContentLoaded", function() {
	sessionStorage.removeItem("session_storage_doc")
});
odoo.define('viin_document.controllerMixin', function (require) {
	"use strict"

	const core = require('web.core');
	var _t = core._t;
	var session = require('web.session');
	var utils = require('web.utils');
	const qweb = core.qweb;
	const config = require('web.config');
	const fileUploadMixin = require('web.fileUploadMixin');
	const ChatterContainer = require('mail/static/src/components/chatter_container/chatter_container.js');
	const { ComponentWrapper } = require('web.OwlCompatibility');
	class ChatterContainerWrapperComponent extends ComponentWrapper {};

	const DocumentViewer = require('viin_document.DocumentDocumentViewer')
	const DocumentEntity = require('viin_document.DocumentEntity')
	const DocumentRightSideBarWidgetOwl = require('viin_document.DocumentRightSideBarWidgetOwl');

	const DocumentControllerMixin = Object.assign({}, fileUploadMixin, {
		events: {
			'click .viin_document_upload': '_onClickDocumentUpload',
			'click .viin_document_add_ink': '_onClickDocumentAddLink',
			'click .btn-toggle-sidebar': '_onToggleSidebar'
		},
		custom_events: Object.assign({}, fileUploadMixin.custom_events, {
			upload_file: '_onUploadFile',
			search_workspace_document: '_onSearchWorkSpaceDocument',
			change_owner_id: '_onChangeOwnerId',
			change_workspace_id: '_onChangeWorkspaceId',
			change_doc_name: '_onChangeDocumentName',
			update_tag: '_onUpdateTag',
			kanban_image_clicked: '_onKanbanPreview',
			open_wizard: '_onOpenWizard',
			handle_document_action: '_onHandleDocumentAction',
			toggle_chatter: '_onToggleViewChatter',
			render_chatter: '_onRenderChatter'
		}),

		/**
		 * @override
		 */
		init: function () {
			this._super.apply(this, arguments);
			fileUploadMixin.init.call(this);
			this.sidebar_widget = new DocumentRightSideBarWidgetOwl()
			this.sidebar_widget.parent = this
			this.max_upload_size = session.max_file_upload_size || 128 * 1024 * 1024
			this.chatter_container = undefined
			this.selected_docs = () => sessionStorage.getItem("session_storage_doc") !== null ? JSON.parse(sessionStorage.getItem("session_storage_doc")) : [];
		},

		/**
		* @override
		*/
		start: function () {
			this._super.apply(this, arguments);
			var self = this;
			this._renderDocumentWidget().then(function (res) {
				self.$('.v_document_content').append(self.$('.v_document_view'));
				self.sidebar_widget.mount(res.find('.v_document_content')[0]).then(function () {
					var $sidebar = self.$('.v_document_content .v_document_right_sidebar_widget');
					$sidebar.after($('<div>', {class: 'v_document_chatter'}).removeClass('show')
						.append($(`<div role="button" class="close-chatter btn btn-sm d-inline-flex d-lg-none
						float-right justify-content-center align-items-center"
						onclick="this.parentNode.classList.toggle('show')"><span class="fa fa-times h3"/>
						</div>`)));
					$sidebar.before($(`<div class='btn btn-toggle-sidebar bg-primary rounded-circle shadow text-white
							d-flex d-lg-none align-items-center justify-content-center'>
							<span class="fa fa-bars"/></div>`)
					);
					self._computeSideBarAndChatterHeight();
				});
			});
		},

		_update: function () {
			this._super.apply(this, arguments);
			this.sidebar_widget.updatePreviewDocuments()
		},

		async reload() {
			await this._renderFileUploads();
		},

		renderButtons($node) {
			this.$buttons = $(qweb.render('DocumentView.buttons'));
            if (!this.model.active_workspace_id) {
                this.$buttons.find('.viin_document_upload, .viin_document_add_ink').prop('disabled', true);
            }
			this.$buttons.appendTo($node);
		},

		_onClickDocumentUpload() {
			/**
			 * Copyright Odoo CE (mrp)
			 * https://github.com/odoo/odoo/blob/14.0/addons/mrp/static/src/js/mrp_documents_controller_mixin.js#L68-L77
			 */
			const $uploadInput = $('<input>', {
				type: 'file',
				name: 'files[]',
				multiple: 'multiple'
			});
			$uploadInput.on('change', async ev => {
				let files = ev.target.files
				for (let file of files){
					if (file.size > this.max_upload_size) {
						var msg = _t("The selected file exceed the maximum file size of %s.");
						this.displayNotification({
							type: 'danger',
							title: _t("File upload"),
							message: _.str.sprintf(msg, utils.human_size(this.max_upload_size))
						});
						return false;
					}
				}
				await this._uploadFiles(files);
				$uploadInput.remove();
			});
			$uploadInput.click();
		},

		_getFileUploadRoute() {
			return '/document/upload_document';
		},

		/**
		 * Copyright Odoo CE (mrp)
		 * https://github.com/odoo/odoo/blob/14.0/addons/mrp/static/src/js/mrp_documents_controller_mixin.js#L102-L104
		 */
		async _onUploadFile(ev) {
			await this._uploadFiles(ev.data.files);
		},

		/**
		 * Copyright Odoo CE (mrp)
		 * https://github.com/odoo/odoo/blob/14.0/addons/mrp/static/src/js/mrp_documents_controller_mixin.js#L52-L58
		 */
		_makeFileUploadFormDataKeys() {
			const context = this.model.get(this.handle, { raw: true }).getContext();
			return {
				workspace_id: this.model.active_workspace_id || null,
				context: context,
			};
		},

		_onClickDocumentAddLink(ev) {
			ev.preventDefault();
			this.do_action('viin_document.document_document_add_link_action', {
				additional_context: {
					'default_workspace_id': this.model.active_workspace_id || null,
				},
				on_close: async () => await this.reload()
			})
		},

		_onToggleSidebar(ev) {
			this._toggleSidebar();
		},

		_toggleSidebar(state) {
			this.$('.v_document_right_sidebar_widget').toggleClass('active', state);
			$('.btn-toggle-sidebar').toggleClass('active', state);
			this._computeSideBarAndChatterHeight();
		},

		_computeSideBarAndChatterHeight() {
			if (config.device.isMobileDevice) {
				const clientHeight = +$('body').height() || 0;
				const docRecordHeight = +this.$('.v_document_view .v_document_kanban').height() || 0;
				const controlPanelHeight = +this.$('.o_control_panel').height() || 0;
				const searchPanelHeight = +this.$('.o_search_panel').height() || 0;
				const mainNavbarHeight = +$('.o_main_navbar').height() || 0;
				const height = clientHeight - (2 * docRecordHeight + controlPanelHeight + searchPanelHeight + mainNavbarHeight + 28);
				this.$('.v_document_right_sidebar_widget').css({
					height: height + 'px'
				});
				this.$('.v_document_chatter').css({
					height: height + 'px'
				});
			}
		},

		_onSearchWorkSpaceDocument(ev) {
			if(ev.data.workspace_id){
				$('.viin_document_upload, .viin_document_add_ink').prop('disabled', false)
			}
			else{
				$('.viin_document_upload, .viin_document_add_ink').prop('disabled', true)
			}
		},

		_onChangeOwnerId (ev) {
			ev.stopPropagation();
			this._updateDocument(
				['owner_id'],
				{
					owner_id: {
						id: ev.data.owner_id,
						action:'CHANGE'
					}
				}
			)
		},

		_onChangeWorkspaceId (ev) {
			ev.stopPropagation();
			this._updateDocument(
				['workspace_id'],
				{
					workspace_id: {
						id: ev.data.workspace_id,
						action:'CHANGE'
					}
				}
			)
		},

		_onChangeDocumentName (ev){
			ev.stopPropagation();
			this._updateDocument(
				['name'],
				{
					name: {
						data: ev.data.name,
						action:'CHANGE'
					}
				}
			)
		},

		_onUpdateTag (ev) {
			let storage_documents = []
			ev.data.doc_ids.forEach(element => {
				let doc = new DocumentEntity(element)
				storage_documents = [...storage_documents, doc]
			});
			sessionStorage.setItem('session_storage_doc', JSON.stringify(storage_documents))
			this.reload({});
		},

		/**
		 * @reference
		 * Copyright Odoo CE (mrp)
		 * https://github.com/odoo/odoo/blob/14.0/addons/mrp/static/src/js/mrp_documents_controller_mixin.js#L88-L93
		 */
		_onKanbanPreview (ev) {
			ev.stopPropagation();
			const documents = ev.data.recordList;
			const documentID = ev.data.recordID;
			const documentViewer = new DocumentViewer(this, documents, documentID);
			documentViewer.appendTo(this.$('.v_document_view'));
		},

		_onOpenWizard(ev){
			let self = this
			let ctx = this.searchModel.get('userId') ? {default_user_id: this.searchModel.get('userId')} : {};
            let doc_ids = this.selected_docs().map(d => {
                return d.doc_id
            })
			self.do_action({
				res_model: 'document.share',
				name: _t('Share Documents URL'),
				type: 'ir.actions.act_window',
				views: [[false, 'form']],
				target: 'new',
				context: _.extend(ctx, {
					default_document_ids: [[6, 0, doc_ids]]
				}),
			});
		},

		_onHandleDocumentAction(ev){
			var self = this
            let doc_ids = this.selected_docs().map(d => {
                return d.doc_id
            })
			this._rpc({
				route: '/document/handle_action',
				params: {
					document_ids: doc_ids,
					action_id:ev.action_id
				},
			}).then(function(result){
				if(result && result.documents){
					let storage_documents = []
					result.documents.forEach(element => {
						let doc = new DocumentEntity(element)
						storage_documents = [...storage_documents, doc]
					});
					sessionStorage.setItem('session_storage_doc', JSON.stringify(storage_documents))
					self.reload({});
				}
			})
		},

		/**
		 * Renders and appends the document right sidebar widget.
		 * @private
		 */
		_renderDocumentWidget: async function () {
			return await this.$('.o_content').append($('<div>').addClass('v_document_content'));
		},

		/**
		 * @param {<Array>} fields
		 * @param {<Object>} value
		 */
		_updateDocument(fields, value){
			let self = this
            let doc_ids = this.selected_docs().map(d => {
                return d.doc_id
            })
			this._rpc({
				route: '/document/update',
				params: {
					data:{
						document_ids: doc_ids,
						fields,
						value
					}
				},
			}).then(function (result) {
				if(result != false){
					let storage_documents = []
					result.forEach(element => {
						let doc = new DocumentEntity(element)
						storage_documents = [...storage_documents, doc]
					});
					sessionStorage.setItem('session_storage_doc', JSON.stringify(storage_documents))
					self.reload({});
				}
			});
		},

		_onRenderChatter(ev){
			self = this
			if (self.chatter_container) {
				self.chatter_container.destroy();
				self.chatter_container = undefined;
			}
			if (this.selected_docs().length === 1) {
				let chatter = new ChatterContainerWrapperComponent(
					this,
					ChatterContainer,
					{
						hasActivities: true,
						hasFollowers: true,
						hasMessageList: true,
						isAttachmentBoxVisibleInitially: true,
						threadId: this.selected_docs()[0].doc_id,
						threadModel: 'document.document',
					}
				);
				chatter.mount(
					self.$('.v_document_chatter')[0]
				).then(function () {
					self.chatter_container = chatter;
				});
			}else{
				$('.v_document_chatter').removeClass('show')
			}
		},

		_onToggleViewChatter(ev) {
			$('.v_document_chatter').toggleClass('show')
		},

		/**
		 * @override
		 */
		_onUploadLoad({xhr}) {
			const result = xhr.status === 200
				? JSON.parse(xhr.response)
				: {
					error: _.str.sprintf(_t("status code: %s </br> message: %s"), xhr.status, xhr.response)
				};
			if (result.error) {
				this.displayNotification({
					type: 'warning',
					title: _t("Failed"),
					message: result.error,
					sticky: true
				})
			}
			fileUploadMixin._onUploadLoad.call(this, ...arguments);
		},
		/**
		 * @override
		 */
		_makeFileUpload(params) {
			return Object.assign(fileUploadMixin._makeFileUpload.call(this, ...arguments), {
				workSpaceId: this.model.active_workspace_id,
			});
		},
		/**
		 * @override
		 */
		_getFileUploadRenderOptions() {
			return {
				predicate: options => !this.model.active_workspace_id || options.workSpaceId === this.model.active_workspace_id,
				targetCallback: fileUploadMixin._getFileUploadRenderOptions.targetCallback
			};
		},
	});

	return DocumentControllerMixin;
})
