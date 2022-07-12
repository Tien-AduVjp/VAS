from odoo import http, _
from odoo.http import request
from odoo.addons.to_website_docs.controllers import editor
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError


class WebsiteDocsEditor(editor.WebsiteDocsEditor):

    def _prepare_document_content_data(self, category):
        data = super(WebsiteDocsEditor, self)._prepare_document_content_data(category)
        odoo_version_id = category.get_matched_odoo_version(odoo_version_str=None)
        if odoo_version_id:
            data.update({
                'odoo_version_id': odoo_version_id.id,
                })
        return data

    def _return_document_content(self, document_content, values={}):
        """
        @param document_content_id: the document record whose value will be prepared for return
        @type document_content_id: website.document.content record
        @param values: dict values
        @rtype: dict
        """
        if document_content.odoo_version_id:
            url = '/docs/%s/d/%s' % (document_content.odoo_version_id.id, slug(document_content.document_id))
        else:
            url = '/docs/d/%s' % slug(document_content.document_id)
        values.update({
            'id': document_content.id,
            'url': url,
            'website_published': document_content.website_published,
            'state': document_content.state
            })
        return values

    @http.route('/docs/add_version', type='json', methods=['POST'], auth="user")
    def add_version(self, res_id, odoo_version_id, current_version_id, **post):
        doc = request.env['website.document'].browse(res_id)
        perms = doc.get_perms()
        if not perms.write:
            editor.permit_denied(doc)
        odoo_version_id = request.env['odoo.version'].browse(odoo_version_id)
        if odoo_version_id:
            for c in doc.content_ids:
                if c.odoo_version_id.id == odoo_version_id.id:
                    return doc.with_context(odoo_version_str=c.odoo_version_id.name).get_website_url()
        current_version_id = request.env['odoo.version'].browse(current_version_id)
        doc_content = doc.with_context(odoo_version_str=current_version_id.name).get_content()
        fulltext = doc_content and doc_content.fulltext or ''
        doc.env['website.document.content'].create({
            'document_id': doc.id,
            'odoo_version_id': odoo_version_id.id,
            'fulltext': fulltext,
        })
        return doc.with_context(odoo_version_str=odoo_version_id.name).get_website_url()

    @http.route('/docs/create', type='json', methods=['POST'], auth="user")
    def create_document(self, category_id, name, **post):
        """
        @param category_id: the id of the category in which the document will be created
        @type category_id: integer
        @param name: the name of the document that will be created
        @type name: string
        """
        category_id = request.env['website.doc.category'].browse(category_id)
        odoo_version_id = post.get('odoo_version_id', False)
        if not category_id:
            editor.permit_denied()
        perms = category_id.document_ids.get_perms()
        if not perms.create:
            editor.permit_denied(category_id)

        if category_id.type != 'category':
            raise ValidationError(_('You are not allowed to create new document in the category in type of %s') % category_id.type)

        doc = request.env['website.document'].sudo().create(self._prepare_document_data(category_id, name))
        if doc and request.env['odoo.version'].browse(odoo_version_id):
            doc.content_ids.write({'odoo_version_id': odoo_version_id})
        return self._return_document(doc)
