from odoo import fields, models, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError, UserError


class WebsiteDocumentContent(models.Model):
    _inherit = "website.document.content"
    _order = 'odoo_version_id'

    odoo_version_id = fields.Many2one('odoo.version', 'Version', index=True, ondelete='restrict', copy=False)

    _sql_constraints = [
        ('version_uniq', 'unique(odoo_version_id, document_id)', 'Odoo Version is already assigned!'),
    ]

    def get_other_odoo_versions(self, check_pubpished=False):
        if not check_pubpished:
            all_versions = self.document_id.content_ids.mapped('odoo_version_id')
        else:
            all_versions = self.document_id.content_ids.filtered(lambda x: x.website_published).mapped('odoo_version_id')
        data = []
        for version in all_versions:
            if version.id != self.odoo_version_id.id or not self.odoo_version_id:
                data.append(version)
        return data

    def get_website_url(self):
        self.ensure_one()
        odoo_version_str = self.odoo_version_id and self.odoo_version_id.name or self.env.context.get('odoo_version_str', '')
        if self.document_id.category_id.document_type == 'hash':
            return '%s#%s' % (self.document_id.category_id.with_context(odoo_version_str=odoo_version_str).get_website_url(), slug(self.document_id))
        if not odoo_version_str:
            return '/docs/d/%s' % (slug(self.document_id))
        return '/docs/%s/d/%s' % (self.odoo_version_id.name, slug(self.document_id))

    def name_get(self):
        result = []
        name = 'no version'
        for r in self:
            if r.odoo_version_id:
                name = 'version ' + r.odoo_version_id.name
            result.append((r.id, name))
        return result

    def _check_published(self):
        for r in self:
            User_Error = False
            if self._context.get('force_write', False):
                if not self.env.user.has_group("to_website_docs.group_website_doc_designer") and r.is_published:
                    User_Error = True
            else:
                if not self.env.user.has_group("to_website_docs.group_website_doc_manager") and r.is_published:
                    User_Error = True
            if User_Error:
                raise UserError(_("You don't have right with this Document Contents '%s' (%s) which is published")%(r.document_id.name, r.odoo_version_id.name))
