var docs_editor_odoo_def = $.Deferred();
window.to_website_doc_defs.push(docs_editor_odoo_def);

odoo.define('to_website_docs_odoo.editor', function(require) {
	'use strict';
	var core = require('web.core');
	var MainPage = require('to_website_docs.editor');
	var ajax = require('web.ajax');
	var QWeb = core.qweb;
	ajax.loadXML('/to_website_docs_odoo/static/src/xml/doc.xml', QWeb);

	MainPage.main_page.include({
		initEditorEvent : function() {
			this._super();
			var me = this;
			me.onVersionEvent();
		},

		onVersionEvent : function() {
			var me = this;
			FE.body.on('click', '.version-editable .dropdown-menu > a', function(e) {
				e.preventDefault();
				var $li = $(this);
				busy(true);
				return myPage.jsonRpc('/docs/add_version', 'call', {
					res_id : $li.data('id'),
					cid: $li.data('cid'),
					odoo_version_id : $li.data('version'),
					current_version_id : ($li.data('current_version')) ? $li.data('current_version') : null,
				}).then(function(result) {
					if (result) {
						window.location = result;
					}
				}).fail(function() {
					setTimeout(function() {
						window.location.reload();
					}, 1000);
				}).always(function() {
					busy(false);
				});
			});
		},

	});

	MainPage.document_dialog.include({
		get_data : function(test) {
			var data = this._super();
			data = _.extend(data, {
				odoo_version_id : this.$("#document-version").val(),
			});
			return data;
		},

		bind_data : function() {
			this._super();
			var $e = this.$("#document-version");
			$e.val(this.data.version_id);
		}
	});

	docs_editor_odoo_def.resolve();

	return MainPage;
});
