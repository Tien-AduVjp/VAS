import logging
from odoo import http, _
from odoo.http import request
from odoo.addons.to_website_docs.controllers import main

_logger = logging.getLogger(__name__)


class WebsiteHelper(main.WebsiteHelper):

    def published(self):
        if self._published is None:
            self._published = request.env['odoo.version'].search([('website_published', '=', True)], limit=1)

    def editor(self):
        if self._editor is None:
            self._editor = request.env['odoo.version'].search([], limit=1)


class WebsiteDocs(main.WebsiteDocs):

    def _prepare_docs_main_page_data(self, **kw):
        data = super(WebsiteDocs, self)._prepare_docs_main_page_data()
        odoo_version_ids = request.env['odoo.version'].search([])
        version_name = kw.get('version', False)
        version = odoo_version_ids.filtered(lambda r:r.name == version_name) if version_name else False
        if not request.env.user.has_group('to_website_docs.group_website_doc_editor'):
            categories = request.website.get_docs_subjects(kw.get('version', odoo_version_ids[:1].name))
            #if not specified, automatically select the available category version published
            i = 1
            while not categories and i != (len(odoo_version_ids) - 1):
                categories = request.website.get_docs_subjects(kw.get('version', odoo_version_ids[i].name))
                i+=1
            odoo_version_ids = request.env['website.document'].search([]).odoo_version_ids
            data.update({'categories': categories})
        data.update({
            'odoo_version_ids': odoo_version_ids,
            'version_ids': odoo_version_ids,
            'version': version or odoo_version_ids.filtered(lambda r:r.recommended)
                       or odoo_version_ids[:1],
        })
        return data

    @http.route(['/docs/<string:version>', '/docs/'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=True)
    def docs(self, **kw):
        return request.render("to_website_docs.docs", self._prepare_docs_main_page_data(**kw))

    def _build_doc_additional_title(self, record, odoo_version):
        """
        For potential inheritance
        """
        return _("%s - Odoo %s") % (record.name, odoo_version.name)

    def _prepare_docs_categ_page_data(self, category, version=False):
        data = super(WebsiteDocs, self)._prepare_docs_categ_page_data(category)
        if version:
            data.update({
                'odoo_version_ids' : version and category.with_context(odoo_version_str=False).search_document().odoo_version_ids,
                'version_ids': version and category.odoo_version_ids or None,
                'version': version,
                'additional_title': self._build_doc_additional_title(category, version),
                })
        return data

    @http.route(['/docs/c/<model("website.doc.category"):category>',
                 '/docs/<string:version>/c/<model("website.doc.category"):category>'],
            type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=True)
    def category(self, category, version=None, **kw):
        """
        Overriding the category method of the parent class
        """
        if version:
            version_record = request.env['odoo.version'].search([('name', '=', version)])
            if not version_record:
                return main.redirect_to_404()
        else:
            odoo_version_ids = category.with_context(odoo_version_str=False).search_document().odoo_version_ids
            if odoo_version_ids:
                url = category.with_context(odoo_version_str=odoo_version_ids[:1].name).get_website_url()
                return request.redirect(url, code=301)

        version = category.get_matched_odoo_version(version)
        if version:
            category = category.with_context(odoo_version_str=version.name)

        if not category.can_view_on_website():
            return main.redirect_to_404()
        category.increase_views()
        return request.render("to_website_docs.docs", self._prepare_docs_categ_page_data(category, version))

    def _prepare_docs_doc_page_data(self, document, odoo_version=False, content=False):
        data = super(WebsiteDocs, self)._prepare_docs_doc_page_data(document, content)
        if odoo_version:
            data.update({
                'main_object': document.get_content(),
                'odoo_version_ids' : data['document'].odoo_version_ids,
                'version_ids': data['document'].odoo_version_ids,
                'version': odoo_version,
                'additional_title': self._build_doc_additional_title(document, odoo_version),
                })
        return data

    @http.route(['/docs/d/<model("website.document"):document>/<int:content_id>',
                 '/docs/d/<model("website.document"):document>',
                 '/docs/<string:version>/d/<model("website.document"):document>'],
            type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=True)
    def document(self, document,content_id=False, version=None, **kw):
        """
        Overriding the document method of the parent class
        """
        # if the current website language is no supported by the document
        # redirect to 404 page
#         if not document._check_lang(request.env.lang):
#             return main.redirect_to_404()

        if not document.can_view_on_website():
            return main.redirect_to_404()

        document_odoo_version_ids = document.odoo_version_ids
        if version:
            version_record = request.env['odoo.version'].search([('name', '=', version)])
            if not version_record or version_record.id not in document_odoo_version_ids.ids:
                if request.env.user.has_group('to_website_docs.group_website_doc_editor'):
                    if document_odoo_version_ids:
                        url = document.get_website_latest_odoo_version_url()
                        return request.redirect(url, code=301)
                return main.redirect_to_404()
        else:
            if document_odoo_version_ids:
                url = document.get_website_latest_odoo_version_url()
                return request.redirect(url, code=301)

        version = document.category_id.get_matched_odoo_version(version)
        if version:
            document = document.with_context(odoo_version_str=version.name)

        # If the document content is not published and the user is neither the creator nor the author nor the author's staff
        # redirect to 404 page
        if not document.get_content().can_view_on_website():
            return main.redirect_to_404()

        sdoc = document.sudo()
        if sdoc.category_id.document_type == 'hash':
            return request.redirect(sdoc.website_url)

        document.increase_views()
        return request.render("to_website_docs.docs", self._prepare_docs_doc_page_data(document, odoo_version=version))

    def _prepare_docs_tag_page_data(self, tag):
        data = super(WebsiteDocs, self)._prepare_docs_tag_page_data(tag)
        data['version'] = None
        return data

    def _prepare_docs_search_page_data(self, search, version, **get):
        domain = self._prepare_docs_search_page_domain(search)
        odoo_version_ids = request.env['website.document'].search([]).odoo_version_ids
        if version:
            domain += [('odoo_version_id.id', '=', int(version))]
        docs = request.env['website.document.content'].search(domain)
        return {
            'search': True,
            'docs': docs,
            'odoo_version_str': version,
            'odoo_version_ids': odoo_version_ids,
            'version_ids': odoo_version_ids,
            'version' : odoo_version_ids.filtered_domain([('id', '=', int(version))])
        }

    @http.route('/docs/search', type='http', website=True,  methods=['GET'], auth="public", sitemap=False)
    def search(self, search, version=False, **get):
        return request.render("to_website_docs.docs", self._prepare_docs_search_page_data(search, version, **get))
