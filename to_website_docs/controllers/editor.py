import logging

from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError
from odoo.http import request
from . import main

_logger = logging.getLogger(__name__)

CATEGORY_UPDATABLE_FIELDS = ['image', 'image_cover', 'color_cover', 'name', 'css_section', 'css_section_item', 'document_type']


def permit_denied(doc=None):
    if doc:
        raise ValidationError(_('Permission denied %s') % doc.name)
    raise ValidationError(_('Permission denied'))


def invalid_data():
    raise ValidationError(_('Invalid data'))


def check_res_model(res_model):
    if res_model not in ['website.document', 'website.doc.category', 'website.document.content']:
        permit_denied()


class WebsiteDocsEditor(http.Controller):

    def _return_category(self, category, values={}):
        """
        @param category: the category record whose value will be prepared for return
        @type category: website.doc.category record 
        @param values: dict values
        @rtype: dict
        """
        values.update({
            'id': category.id,
            'url': '#' if category.type == 'section' else category.website_url,
            'website_published': category.website_published
            })
        return values

    def _return_document(self, document, values={}):
        """
        @param document: the document record whose value will be prepared for return
        @type document: website.document record 
        @param values: dict values
        @rtype: dict
        """
        values.update({
            'id': document.id,
            'url': '/docs/d/%s' % slug(document),
            'website_published': document.website_published,
            'state': document.state
            })
        return values
    
    def _return_document_content(self, document_content, values={}):
        """
        @param document_content_id: the document record whose value will be prepared for return
        @type document_content_id: website.document.content record 
        @param values: dict values
        @rtype: dict
        """
        values.update({
            'id': document_content.id,
            'url': '/docs/d/%s' % slug(document_content.document_id),
            'website_published': document_content.website_published,
            'state': document_content.state
            })
        return values

    def _prepare_document_content_data(self, category):
        return {
            'fulltext': '',
            }

    def _prepare_document_data(self, category, name):
        user = category.env.user
        return {
            'category_id': category.id,
            'name': name,
            'content_ids': [(0, 0, self._prepare_document_content_data(category))],
            'user_id': user.id,
            'author_id': user and user.partner_id.id or False
            }

    @http.route('/docs/create', type='json', methods=['POST'], auth="user")
    def create_document(self, category_id, name, **post):
        """
        @param category_id: the id of the category in which the document will be created
        @type category_id: integer
        @param name: the name of the document that will be created
        @type name: string
        """
        category_id = request.env['website.doc.category'].browse(category_id)
        if not category_id:
            permit_denied()
        perms = category_id.document_ids.get_perms()
        if not perms.create:
            permit_denied(category_id)

        if category_id.type != 'category':
            raise ValidationError(_('You are not allowed to create new document in the category in type of %s') % category_id.type)

        doc = request.env['website.document'].sudo().create(self._prepare_document_data(category_id, name))
        return self._return_document(doc)

    @http.route('/docs/create_category', type='json', methods=['POST'], auth="user")
    def create_category(self, name, parent_id=False, **post):
        """
        @param name: the name of the to-be-created category
        @type name: string
        @param parent_id: the id of the parent category of the to-be-created category
        @type parent_id: int | False
        """
        website_helper = main.WebsiteHelper()
        category_type = 'subject'
        user = request.env.user
        if parent_id:
            parent_id = request.env['website.doc.category'].browse(int(parent_id))
            if parent_id.type == 'category':
                invalid_data()
            elif parent_id.type == 'subject':
                if not website_helper.is_website_doc_reviewer():
                    permit_denied(parent_id)
                category_type = 'section'
            elif parent_id.type == 'section':
                perms = parent_id.get_perms()
                if not perms.write:
                    permit_denied(parent_id)
                category_type = 'category'
        elif not website_helper.is_website_doc_manager():
            permit_denied()

        category = request.env['website.doc.category'].create({
            'name': name,
            'parent_id': parent_id and parent_id.id,
            'author_id': user.partner_id.id,
            'type': category_type,
            'lang_ids': parent_id and [(6, 0, parent_id.lang_ids.ids)] or False
        })
        if category.parent_id:
            category._onchange_parent_id()
        values = self._return_category(category)
        if category.parent_id:
            values['url'] = "#"
        return values

    @http.route('/docs/update_document', type='json', methods=['POST'], auth="user")
    def update_document(self, document_id, **post):
        """
        @param document_id: the id of the website.document record to update
        @type document_id: integer
        @param post: dictionary of field->val for document update
        @type post: dict
        """
        document_id = request.env['website.document'].browse(document_id)
        perms = document_id.get_perms()
        if not perms.write:
            permit_denied(document_id)
        if 'name' in post:
            document_id.write({'name':post['name']})
        return self._return_document(document_id)

    @http.route('/docs/update_category', type='json', methods=['POST'], auth="user")
    def update_category(self, category_id, **post):
        """
        @param category_id: the id of the to-be-updated category
        @type category_id: integer
        @param post: the dictionary of field->val for updating the category
        @param post: dict
        """
        category_id = request.env['website.doc.category'].browse(category_id)
        perms = category_id.get_perms()
        if not perms.write:
            permit_denied(category_id)

        return_vals = {}
        hasName = False

        categ_update_data = {}
        for f in CATEGORY_UPDATABLE_FIELDS:
            if f in post:
                categ_update_data[f] = post[f]

                if f == 'color_cover':
                    return_vals['color_cover'] = category_id.get_color()
                elif f == 'name':
                    hasName = True
                elif f == 'document_type' and category_id.type != 'category':
                    invalid_data()

        if bool(categ_update_data):
            category_id.write(categ_update_data)
            return_vals['color_cover'] = category_id.get_color()
        return_vals = self._return_category(category_id, values=return_vals)
        if hasName:
            return_vals['url'] = '#'
        return return_vals

    @http.route('/docs/delete', type='json', methods=['POST'], auth="user")
    def action_context_delete(self, res_id, res_model, **post):
        """
        Delete either the category or the document, according to the website context
        @param res_id: the id of the record to delete
        @type res_id: integer
        @param res_model: the model of the record to delete
        @type res_model: string
        """
        # Check if the res_model is allowed for deletion
        check_res_model(res_model)
        record = request.env[res_model].browse(res_id)
        perms = record.get_perms()
        if not perms.unlink:
            permit_denied(record)

        # prepare return URL
        res = '/docs'
        if res_model == 'website.doc.category':
            if record.parent_id:
                res = record.parent_id.website_url
        elif res_model == 'website.document':
            res = record.category_id.website_url
        record.unlink()
        return res

    @http.route('/docs/change_status', type='json', methods=['POST'], auth="user")
    def change_status(self, res_id, res_model, state, published=False, **post):
        # Check if the res_model is allowed for status change
        check_res_model(res_model)
        document = request.env[res_model].browse(res_id)
        perms = document.get_perms()
        if not perms.write or (state in ['approved', 'draft'] and not perms.approve):
            permit_denied(document)

        if state == 'confirmed':
            document.action_confirm()
        elif state == 'approved':
            # confirm the document first
            if document.state == 'draft':
                document.action_confirm()
            # then approve it
            if document.state == 'confirmed':
                document.action_approve()
            if published == True:
                document.action_publish()

        elif state == 'draft':
            document.action_draft()
        elif state == 'cancelled':
            document.action_cancel()

        # publish the document
        if published and document.state == 'approved' and not document.website_published:
            if not perms.approve:
                permit_denied(document)

            document.action_publish_toggle()

        if res_model == 'website.document':
            return self._return_document(document)
        elif res_model == 'website.document.content':
            return self._return_document_content(document)
        return self._return_category(document)

    @http.route('/docs/toggle_published', type='json', methods=['POST'], auth="user")
    def toggle_published(self, res_id, res_model, publish, **post):
        # Check if the res_model is allowed for toggling published
        check_res_model(res_model)
        document = request.env[res_model].browse(res_id)
        perms = document.get_perms()
        if not perms.approve:
            permit_denied(document)

        document.action_publish_toggle()

        if res_model == 'website.document':
            return self._return_document(document)
        elif res_model == 'website.document.content':
            return self._return_document_content(document)
        return self._return_category(document)

    @http.route('/docs/search_tags', type='json', methods=['POST'], auth="user")
    def search_tags(self, res_id, res_model, search, **post):
        # Check if the res_model is allowed for search
        check_res_model(res_model)
        document = request.env[res_model].browse(res_id)
        domain = [('name', 'ilike', search)]
        if document.tag_ids:
            domain += [('id', 'not in', document.tag_ids.ids)]
        tags = request.env['website.doc.tag'].search(domain, limit=10)
        data = []
        for c in tags:
            data.append({
                'id': c.id,
                'name': c.name,
                'url': '/docs/t/%s' % slug(c)
            })
        return {
            'key': search,
            'data': data
        }

    @http.route('/docs/add_tags', type='json', methods=['POST'], auth="user")
    def add_tags(self, res_id, res_model, name, tag=None, **post):
        """
        Create a new or assign and existing tag base on the input tag name

        @param res_id: integer id of the resource (e.g. document, category)
        @param res_model: which is either 'website.doc.category' or 'website.document'
        @param name: the name of the tag to be assign
        @param tag: the id of an existing tag (int)
        """
        # Check if the res_model is allowed for assignment
        check_res_model(res_model)

        # browse the document/category for which the tag will be created/assigned for
        document = request.env[res_model].browse(res_id)

        perms = document.get_perms()
        if not perms.write:
            raise ValidationError(_("You don't have appropriate permission to assign tag to the %s") % document.name)

        name = name.strip()
        Tag = request.env['website.doc.tag']
        if tag:
            tag = Tag.browse(int(tag))
        else:
            # Search for an existing tag
            tags = Tag.search([('name', 'ilike', name)]).filtered(lambda t: t.name.lower() == name.lower())
            if tags:
                tag = tags[0]

        # create a new tag if no exist found
        if not tag:
            tag = Tag.sudo().create({
                'name': name
            })

        # ignore if the tag has been assigned already
        if tag in document.tag_ids:
            return False

        # assign the tag to the record
        document.write({
            'tag_ids': [(4, tag.id)]
        })
        return {
            'id': tag.id,
            'name': tag.name,
            'url': '/docs/t/%s' % slug(tag)
        }

    @http.route('/docs/remove_tags', type='json', methods=['POST'], auth="user")
    def remove_tags(self, res_id, res_model, tag, **post):
        # Check if the res_model is allowed for removing tags
        check_res_model(res_model)
        document = request.env[res_model].browse(res_id)
        perms = document.get_perms()
        if not perms.write:
            permit_denied(document)

        tag = request.env['website.doc.tag'].browse(int(tag))
        document.write({
            'tag_ids': [(3, tag.id)]
        })
        return True

    @http.route('/docs/resequence', type='json', methods=['POST'], auth="user")
    def resequence(self, ids, category, parent=None, **post):
        if len(ids) <= 1:
            invalid_data()
        category = request.env['website.doc.category'].browse(category)
        perms = category.get_perms()
        if not perms.create:
            permit_denied(category)

        if parent:
            parent = request.env['website.document'].browse(parent)
            perms = parent.get_perms()
            if not perms.write:
                permit_denied(parent)

        docs = request.env['website.document'].search([(('id', 'in', ids))])
        if len(docs) != len(ids):
            invalid_data()

        sequences = []
        for d in docs:
            if parent:
                if d.parent_id != parent:
                    invalid_data()
            elif d.category_id != category:
                invalid_data()
            sequences.append(d.sequence)

        seq = 0
        for idx, val in enumerate(ids):
            for d in docs:
                if d.id == val:
                    d.sequence = sequences[idx]
                    if d.sequence <= seq:
                        d.sequence = seq + 1
                    seq = d.sequence
                    break
        return True

    @http.route('/docs/resequence_category', type='json', methods=['POST'], auth="user")
    def resequence_category(self, ids, parent=None, **post):
        if len(ids) <= 1:
            invalid_data()

        Category = request.env['website.doc.category']
        website_helper = main.WebsiteHelper()
        if not parent:
            if not website_helper.is_website_doc_manager():
                permit_denied()
        else:
            parent = Category.browse(parent)
            if parent.type != 'subject':
                perms = parent.get_perms()
                if not perms.write:
                    permit_denied(parent)

        docs = Category.search([(('id', 'in', ids))])
        if len(docs) != len(ids):
            invalid_data()

        sequences = []
        for d in docs:
            if parent:
                if d.parent_id != parent:
                    invalid_data()
                if parent.type == 'subject':
                    perms = d.get_perms()
                    if not perms.write:
                        permit_denied(d)
            sequences.append(d.sequence)

        seq = 0
        for idx, val in enumerate(ids):
            for d in docs:
                if d.id == val:
                    d.sequence = sequences[idx]
                    if d.sequence <= seq:
                        d.sequence = seq + 1
                    seq = d.sequence
                    break
        return True

    @http.route('/docs/view_edit', type='json', methods=['POST'], auth="user")
    def edit_category(self, res_id, res_model, **post):
        # Check if the res_model is allowed for edit
        check_res_model(res_model)
        doc = request.env[res_model].browse(res_id)
        perms = doc.get_perms()
        if not perms.write:
            permit_denied(doc)
        if res_model == 'website.doc.category':
            if doc.type == 'subject':
                action_id = 'to_website_docs.subject_action'
            elif doc.type == 'section':
                action_id = 'to_website_docs.section_action'
            else:
                action_id = 'to_website_docs.category_action'
        elif res_model == 'website.document.content':
            action_id = 'to_website_docs.document_content_action'
        else:
            action_id = 'to_website_docs.document_action'
        action_id = doc.env.ref(action_id).id
        return '/web#id=%s&view_type=form&model=%s&action=%s' % (res_id, res_model, action_id)
