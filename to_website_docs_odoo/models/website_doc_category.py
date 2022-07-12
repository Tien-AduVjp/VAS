from odoo import fields, models, api
from odoo.addons.http_routing.models.ir_http import slug


class WebsiteDocCategory(models.Model):
    _inherit = 'website.doc.category'

    @api.model
    def _get_default_version(self):
        return self.env['odoo.version'].search([], limit=1)

    odoo_version_ids = fields.Many2many('odoo.version', 'odoo_version_website_doc_category_rel', 'category_id', 'odoo_version_id', string='Odoo Versions',
                                        compute='_compute_odoo_versions', store=True,
                                        default=_get_default_version)

    @api.depends('child_ids', 'child_ids.odoo_version_ids',
                 'document_ids', 'document_ids.content_ids', 'document_ids.content_ids.odoo_version_id')
    def _compute_odoo_versions(self):
        for r in self:
            odoo_version_ids = r.document_ids.mapped('content_ids.odoo_version_id')
            if r.child_ids:
                odoo_version_ids |= r.child_ids.mapped('odoo_version_ids')
            r.odoo_version_ids = [(6, 0, odoo_version_ids.ids)]

    def get_website_url(self):
        self.ensure_one()
        res = super(WebsiteDocCategory, self).get_website_url()
        odoo_version_str = self._context.get('odoo_version_str', '')
        if self.type == 'category':
            if not odoo_version_str and self.odoo_version_ids:
                odoo_version_str = self.odoo_version_ids[:1].name

        if odoo_version_str:
            res = '/docs/%s/c/%s' % (odoo_version_str, slug(self))

        return res

    def get_matched_odoo_version(self, odoo_version_str=None):
        """
        @param odoo_version_str: odoo version string

        @return: odoo.version record
        @rtype: odoo.version
        """
        if not odoo_version_str:
            return self.odoo_version_ids[:1]
        # find the first matched version in the category
        return self.env['odoo.version'].search([('name', '=', odoo_version_str)], limit=1)

    def _prepare_documents_domain(self):
        domain = super(WebsiteDocCategory, self)._prepare_documents_domain()

        odoo_version_str = self._context.get('odoo_version_str', False)
        if odoo_version_str:
            domain += [('content_ids.odoo_version_id.name', '=', odoo_version_str)]
        return domain

    def search_document(self):
        """
        Search for all the documents that belong to the current categories  (self)
        @rtype: website.document
        """
        user = self.env.user
        if not user.has_group('to_website_docs.group_website_doc_editor'):
            domain = self._prepare_documents_domain()
            document = self.env['website.document'].search(domain)
            odoo_version_str = self._context.get('odoo_version_str', False)
            if odoo_version_str:
                contents = document.mapped('content_ids').filtered(lambda c: c.website_published and c.odoo_version_id.name == odoo_version_str)
            else:
                contents = document.mapped('content_ids').filtered(lambda c: c.website_published)
            return contents.document_id
        else:
            return super(WebsiteDocCategory, self).search_document()
