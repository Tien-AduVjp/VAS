import logging

from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import Website
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


def redirect_to_404():
    return request.render('website.page_404')


class WebsiteHelper():
    _published = None
    _editor = None

    def __init__(self):
        self.is_website_doc_editor = request.env.user.has_group('to_website_docs.group_website_doc_editor')
        self.base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

    def is_website_doc_manager(self):
        return request.env.user.has_group('to_website_docs.group_website_doc_manager')

    def is_website_doc_reviewer(self):
        return request.env.user.has_group('to_website_docs.group_website_doc_reviewer')


class Website(Website):

    @http.route(['/website/publish'], type='json', auth="public", website=True)
    def publish(self, id, object):

        if object == 'website.document' or object == 'website.document.content':
            # TODO: raise a warning here to ask the user to use the tool of the application instead
            Model = request.env[object]
            document = Model.browse(int(id))
            if document.state == 'approved':
                perms = document.get_perms()
                if not perms.approve:
                    display_name = ''
                    if object == 'website.document':
                        display_name = document.name
                    else:
                        display_name = document.document_id.name
                    raise ValidationError(_('Permission denied %s')%display_name)
                document.action_publish_toggle()
            else:
                raise ValidationError(_("The feature is disabled!"))
            return bool(document.website_published)
            
        if object == 'website.doc.category':
            Model = request.env[object]
            category = Model.browse(int(id))
            perms = category.get_perms()
            if not perms.approve :
                raise ValidationError(_('Permission denied %s') % category.name)
            category.action_publish_toggle()
            return bool(category.website_published)
        return super(Website, self).publish(id, object)

class WebsiteDocs(http.Controller):

    def _prepare_docs_main_page_data(self, **kw):
        website_helper = WebsiteHelper()
        categories = request.website.get_docs_subjects()
        role_type = request.website.get_role_category()
        return {
            'category': None,
            'categories': categories,
            'role_type':role_type,
            'subjects': categories,
            'website_helper': website_helper,
            'is_website_doc_editor': website_helper.is_website_doc_editor,
            'slug': slug
        }

    @http.route([ '/docs'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def docs(self, **kw):
        return request.render("to_website_docs.docs", self._prepare_docs_main_page_data(**kw))

    def _prepare_docs_categ_page_data(self, category):
        website_helper = WebsiteHelper()
        domain = [('parent_id', '=', category.id)] + request.website._prepare_docs_categ_domain()
        categories = category.search(domain)
        role_type = request.website.get_role_category()
        return {
            'main_object': category,
            'category': category,
            'categories': categories,
            'role_type':role_type,
            'subjects': request.website.get_docs_subjects(),
            'website_helper': website_helper,
            'is_website_doc_editor': website_helper.is_website_doc_editor,
            'slug': slug
        }

    @http.route(['/docs/c/<model("website.doc.category"):category>'],
            type='http', methods=['GET', 'POST'], auth="public", website=True)
    def category(self, category, **kw):
        if not category.can_view_on_website():
            return redirect_to_404()
        
        categ_website_id = category._find_website()

        if categ_website_id and categ_website_id != request.website:
            return redirect_to_404()

        category.increase_views()
        return request.render("to_website_docs.docs", self._prepare_docs_categ_page_data(category))

    def _prepare_docs_doc_page_data(self, document, content):
        website_helper = WebsiteHelper()
        role_type = request.website.get_role_category()
        return {
            'document': document,
            'content': content or document.get_content(),
            'main_object': content or document.get_content(),
            'category': document.category_id,
            'categories': document.category_id,
            'role_type': role_type,
            'subjects': request.website.get_docs_subjects(),
            'website_helper': website_helper,
            'is_website_doc_editor': website_helper.is_website_doc_editor,
            'slug': slug
        }

    @http.route(['/docs/d/<model("website.document"):document>/<int:content_id>',
                 '/docs/d/<model("website.document"):document>'],
            type='http', methods=['GET', 'POST'], auth="public", website=True)
    def document(self, document,content_id=False , **kw):
        # if the current website language is no supported by the document
        # redirect to 404 page
#         if not document._check_lang(request.env.lang):
#             return redirect_to_404()

        # If the document is not published and the user is neither the creator nor the author nor the author's staff
        # redirect to 404 page
        if not document.can_view_on_website():
            return redirect_to_404()

        if document.website_id and document.website_id != request.website:
            return redirect_to_404()

        sdoc = document.sudo()
        if sdoc.category_id.document_type == 'hash':
            return request.redirect(sdoc.website_url)

        document.increase_views()
        if content_id in document.content_ids.ids:
            content = request.env["website.document.content"].browse([content_id])
            if content.exists():
                return request.render("to_website_docs.docs", self._prepare_docs_doc_page_data(document,content=content))
        return request.render("to_website_docs.docs", self._prepare_docs_doc_page_data(document,content=False))

    def _prepare_docs_tag_page_data(self, tag):
        website_helper = WebsiteHelper()
        domain = [('tag_ids', 'in', [tag.id]), '|',
                    ('lang_ids.code', 'in', [request.env.lang]),
                    ('lang_ids', '=', False)]
        if not request.env.user.has_group('to_website_docs.group_website_doc_editor'):
            domain.append(('is_published', '=', True))
        
        role_type = request.website.get_role_category()
        return {
            'tag': tag,
            'main_object': tag,
            'category': None,
            'documents': request.env['website.document'].search(domain),
            'categories': request.env['website.doc.category'].search(domain + [('document_type', '=', 'hash')]),
            'role_type': role_type,
            'subjects': request.website.get_docs_subjects(),
            'website_helper': website_helper,
            'is_website_doc_editor': website_helper.is_website_doc_editor,
            'slug': slug
            }

    @http.route(['/docs/t/<model("website.doc.tag"):tag>'],
            type='http', methods=['GET', 'POST'], auth="public", website=True)
    def tags(self, tag, **kw):
        return request.render("to_website_docs.docs", self._prepare_docs_tag_page_data(tag))

    def _prepare_docs_search_page_domain(self, search):
        domain = ['|', '|', '|',
                  ('document_id.name', 'ilike', search),
                  ('document_id.tag_ids.name', 'ilike', search),
                  ('fulltext', 'ilike', search),
                  ('document_id.category_id.name', 'ilike', search),
                  ]
        user = request.env.user
        if not user.has_group('to_website_docs.group_website_doc_editor'):
            domain += [
                '|', ('website_published', '=', True),
                '&', ('website_published', '=', False),
                '|', ('create_uid', '=', user.id), ('author_id', '=', user.partner_id.commercial_partner_id.id)]
        return domain

    def _prepare_docs_search_page_data(self, search, **get):
        domain = self._prepare_docs_search_page_domain(search)
        docs = request.env['website.document.content'].search(domain)
        return {'search': True, 'docs': docs}

    @http.route('/docs/search', type='http', website=True,  methods=['GET'], auth="public")
    def search(self, search, **get):
        return request.render("to_website_docs.docs", self._prepare_docs_search_page_data(search, **get))
