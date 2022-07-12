odoo.define('viin_document.DocumentListView', function (require) {
	"use strict";

	const ListView = require('web.ListView');
	const view_registry = require('web.view_registry');
	const DocumentListModel = require('viin_document.DocumentListModel');
	const DocumentListController = require('viin_document.DocumentListController');
	const DocumentListRenderer = require('viin_document.DocumentListRenderer')

	const DocumentListView = ListView.extend({
		config: _.extend({}, ListView.prototype.config, {
			Model: DocumentListModel,
			Controller: DocumentListController,
			Renderer: DocumentListRenderer
		})
	});

	view_registry.add('document_list', DocumentListView);

	return DocumentListView;
})
