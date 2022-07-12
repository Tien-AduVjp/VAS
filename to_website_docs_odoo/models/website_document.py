from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.http_routing.models.ir_http import slug


class WebsiteDocument(models.Model):
    _inherit = 'website.document'

    odoo_version_ids = fields.Many2many('odoo.version', string='Odoo Versions', compute='_compute_odoo_versions',
                                        help="The Odoo Versions related to this document")
    unassigned_odoo_version_ids = fields.Many2many('odoo.version', string='Unassigned Odoo Versions', compute='_compute_odoo_versions',
                                                   help="The Odoo Versions that are not related to this document")

    @api.model
    def _get_default_version(self):
        return self.env['odoo.version'].search([], limit=1)

    def _compute_odoo_versions(self):
        all_odoo_versions = self.env['odoo.version'].search([])
        for r in self:
            if not self.env.user.has_group('to_website_docs.group_website_doc_editor'):
                assigned_odoo_version_ids = r.content_ids.filtered(lambda c: c.website_published or
                                                                         c.get_perms(c.document_id.category_id).write).odoo_version_id
            else:
                assigned_odoo_version_ids = r.content_ids.mapped('odoo_version_id')
            r.update({
                'odoo_version_ids': assigned_odoo_version_ids.ids,
                'unassigned_odoo_version_ids': (all_odoo_versions - assigned_odoo_version_ids).ids
                })

    def get_website_url(self):
        self.ensure_one()
        odoo_version_str = self._context.get('odoo_version_str', '')
        if self.category_id.document_type == 'hash':
            return '%s#%s' % (self.category_id.with_context(odoo_version_str=odoo_version_str).get_website_url(), slug(self))
        else:
            if odoo_version_str:
                return '/docs/%s/d/%s' % (odoo_version_str, slug(self))
            else:
                return '/docs/d/%s' % slug(self)


    def get_website_latest_odoo_version_url(self):
        self.ensure_one()
        odoo_versions = self.odoo_version_ids
        if odoo_versions:
            url = self.with_context(odoo_version_str=odoo_versions[0].name).get_website_url()
        else:
            url = self.get_website_url()
        return url

    def _prepare_content_domain(self):
        domain = super(WebsiteDocument, self)._prepare_content_domain()
        odoo_version_str = self._context.get('odoo_version_str', '')
        if odoo_version_str:
            domain += [('odoo_version_id.name', '=', odoo_version_str)]
        return domain

    def get_content(self):
        self.ensure_one()

        WebsiteDocumentContent = self.env['website.document.content']
        content_id = super(WebsiteDocument, self).get_content()
        if not content_id:
            content_id = WebsiteDocumentContent.search([('document_id', '=', self.id), ('odoo_version_id', '=', False)], limit=1)
            if not content_id:
                content_id = WebsiteDocumentContent.create({'document_id': self.id, 'fulltext': "<br/><br/>"})
        return content_id

    @api.model
    def _validate_merge(self, dest_document):
        super(WebsiteDocument, self)._validate_merge(dest_document)
        dest_odoo_version_ids = dest_document.content_ids.mapped('odoo_version_id')
        for content_id in self.content_ids:
            if content_id.odoo_version_id.id in dest_odoo_version_ids.ids:
                raise ValidationError(_("The source document contains a content in Odoo version %s which"
                                        " is already available in the destination content. You must remove"
                                        " one from either before proceeding.") % content_id.odoo_version_id.name)
