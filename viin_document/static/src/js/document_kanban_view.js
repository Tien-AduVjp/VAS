odoo.define('viin_document.DocumentKanbanView', function (require) {
	"use strict";

	const KanbanView = require('web.KanbanView');
	const view_registry = require('web.view_registry');
	const DocumentKanbanController = require('viin_document.DocumentKanbanController');
	const DocumentKanbanRender = require('viin_document.DocumentKanbanRenderer');
	const DocumentKanbanModel = require('viin_document.DocumentKanbanModel');

	const DocumentKanbanView = KanbanView.extend({
		config: _.extend({}, KanbanView.prototype.config, {
			Model: DocumentKanbanModel,
			Controller: DocumentKanbanController,
			Renderer: DocumentKanbanRender
		})
	});

	view_registry.add('document_kanban', DocumentKanbanView);

	return DocumentKanbanView;
})
