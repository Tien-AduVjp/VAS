import lxml.html
import lxml.etree as et

from odoo import fields, models, api, _
from odoo.tools.translate import html_translate
from odoo.exceptions import ValidationError, UserError
from odoo.addons.http_routing.models.ir_http import slug
from . import document_permission


class WebsiteDocumentContent(models.Model):
    _name = "website.document.content"
    _description = "Website Document Content"
    _inherit = ['mail.thread', 'website.seo.metadata', 'website.published.mixin', 'abstract.website.doc', 'mail.activity.mixin']

    document_id = fields.Many2one('website.document', 'Document', index=True, ondelete='cascade', required=True)
    introtext = fields.Html('Intro Text', compute='_get_introtext', translate=html_translate,
                            help="This field extracts content from full text for document intro on website document list")
    introtext_length = fields.Integer(related='document_id.introtext_length', store=True, readonly=True)
    fulltext = fields.Html('Full Text', translate=html_translate, help="Stores HTML content that could be created from website frontend (using drag/drop)")
    date_published = fields.Date('Published Date', readonly=True, tracking=True, help="Once published, this field will keep unchanged forever")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')], 'Status', default='draft', index=True, copy=False, tracking=True)
    validator_id = fields.Many2one('res.users', 'Validated by', tracking=True)
    user_id = fields.Many2one('res.users', 'Assigned to', related='document_id.user_id')
    website_id = fields.Many2one(related='document_id.website_id', store=True, index=True)
    author_id = fields.Many2one('res.partner', copy=False)

    def _get_introtext(self):
        fulltext_data = self.read(['fulltext', 'introtext_length'])
        mapped_data = dict([(el['id'], self._build_introtext(el['fulltext'], el['introtext_length'])) for el in fulltext_data])
        for r in self:
            r.introtext = mapped_data.get(r.id, '')

    def _build_introtext(self, fulltext, intro_length=300):
        try:
            fulltext = lxml.html.document_fromstring(fulltext)
            fulltext = fulltext.text_content()
            return fulltext[:intro_length] + '...'
        except Exception as e:
            return ''

    def _add_id_to_h_tags(self, html_str):
        try:
            idx = 0
            html = lxml.html.document_fromstring(html_str)
            titles = html.xpath('//*[local-name() = "h2" or local-name() = "h3"]')
            for title in titles:
                idx += 1
                if title.text:
                    tag_id = title.text.replace(' ', '-').lower() + '-' + str(idx)
                    title.attrib['id'] = tag_id
            if len(titles):
                return et.tostring(html, encoding='unicode')
        except Exception as e:
            return html_str
        return html_str

    def _generate_indexes_from_h_tags(self):
        childs = []
        try:
            idx = 0
            html = lxml.html.document_fromstring(self.fulltext)
            titles = html.xpath('//*[local-name() = "h2" or local-name() = "h3"]')
            child = {'name':'', 'childs': []}
            for title in titles:
                idx = idx + 1
                child_dict = {}
                if title.text and 'id' in title.attrib:
                    child_dict.update({
                        'name': title.text,
                        'id': title.attrib['id']
                        })
                if title.tag == 'h2':
                    if child['name']:
                        childs.append(child)
                        child = {'name':'', 'childs': []}
                    child.update(child_dict)
                else:
                    if child['name'] and bool(child_dict):
                        child['childs'].append(child_dict)
            if child['name']:
                childs.append(child)
        except Exception as e:
            return childs
        return childs

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            fulltext = vals.get('fulltext', False)
            if fulltext:
                vals['fulltext'] = self._add_id_to_h_tags(vals['fulltext'])
        return super(WebsiteDocumentContent, self).create(vals_list)

    def write(self, vals):
        self.with_context(force_write=True)._check_published()
        for r in self:
            author = r.author_id.user_ids.filtered(lambda u:u.company_id == self.env.company)
            if author != self.env.user:
                r.document_id._check_role()
        if 'fulltext' in vals:
            vals['fulltext'] = self._add_id_to_h_tags(vals['fulltext'])
        return super(WebsiteDocumentContent, self).write(vals)

    def unlink(self):
        self._check_published()
        for r in self:
            author = r.author_id.user_ids.filtered(lambda u:u.company_id == self.env.company)
            if author != self.env.user:
                r.document_id._check_role(delete=True)
        document_ids = self.mapped('document_id')
        res = super(WebsiteDocumentContent, self).unlink()
        if self._context.get('remove_empty_document', False):
            documents_to_delete = document_ids.filtered(lambda d: not d.content_ids)
            if documents_to_delete:
                documents_to_delete.unlink()
        return res

    def action_confirm(self):
        for r in self:
            if r.state not in ('draft', 'rejected'):
                raise UserError(_("You cannot confirm this document content while its state is neither Draft nor Rejected."))
        self.write({'state': 'confirmed'})

    def action_reject(self):
        if not self.env.user.has_group('to_website_docs.group_website_doc_reviewer'):
            self.document_id._raise_documents('to_website_docs.group_website_doc_reviewer')
        for r in self:
            if r.state != 'confirmed':
                raise UserError(_("You cannot reject this document content while its state is not Confirmed."))
        self.write({'state': 'rejected'})

    def action_reconfirm(self):
        for r in self:
            if r.state not in ('draft', 'rejected'):
                raise UserError(_("You cannot reconfirm this document content while its state is neither Draft nor Rejected."))
        self.write({'state': 'confirmed'})

    def action_approve(self):
        if not self.env.user.has_group('to_website_docs.group_website_doc_reviewer'):
            self.document_id._raise_documents('to_website_docs.group_website_doc_reviewer')
        for r in self:
            if r.document_id.state != 'approved':
                raise UserError(_("You should approve the document '%s' first.") % (r.document_id.name))
            if r.state not in ('draft', 'confirmed', 'rejected'):
                raise UserError(_("You cannot approve this document content while its state is neither Draft nor Confirmed nor Rejected."))

        self.write({
            'validator_id': self.env.user.id,
            'state': 'approved',
            })

    def action_cancel(self):
        self.action_unpublish()
        self.write({'state':'cancelled'})

    def action_draft(self):
        if not self.env.user.has_group('to_website_docs.group_website_doc_reviewer'):
            self.document_id._raise_documents('to_website_docs.group_website_doc_reviewer')
        for r in self:
            if r.state != 'cancelled':
                raise UserError(_("You cannot set this document content to Draft while its state is not Cancelled."))
        self.write({'state': 'draft'})

    def action_publish(self):
        """
        If the context contain `forced_published_date`, it will be used as the date_published instead of the current date
        """
        if not self.env.user.has_group('to_website_docs.group_website_doc_designer'):
            raise ValidationError(_("You must has '%s' access right to publish website documents.")
                                  % (self.env.ref('to_website_docs.group_website_doc_designer').name,))
        for r in self:
            if r.state != 'approved':
                raise UserError(_("You cannot publish this document content while its state is not Approved."))
        # already published once, we will not update the published date anymore
        self.filtered(lambda d: d.website_published == False and d.date_published).write({'website_published': True})
        # set published date for ones that have never been published
        self.filtered(lambda d: d.website_published == False and not d.date_published).write({
            'website_published': True,
            'date_published': self._context.get('forced_published_date', fields.Date.today())
            })
        # publish its categories recursively also. Otherwise it does not make sense when the document is publish inside a unpublished category
        self.mapped('document_id').filtered(lambda c: not c.website_published).action_publish_toggle()

    def action_unpublish(self):
        contents_published = self.filtered('website_published')
        if contents_published:
            if not self.env.user.has_group('to_website_docs.group_website_doc_manager'):
                raise UserError(_("The Document Contents is published. Only Docs Manager has rights unpublish this document Content."))
            contents_published.write({'website_published': False})
        #unpublish document if all document content unpublish
        if not self.document_id.filtered_domain([('content_ids.website_published', '=', True)]):
            self.document_id.action_unpublish()

    def action_publish_toggle(self):
        """
        To be called from website frontend via controller
        """
        to_unpublish = self.filtered(lambda d: d.website_published)
        if to_unpublish:
            to_unpublish.action_unpublish()
        to_publish = self - to_unpublish
        if to_publish:
            to_publish.action_publish()

    def website_publish_button(self):
        result = super(WebsiteDocumentContent, self).website_publish_button()
        self.action_publish_toggle()
        return result

    def website_view_button(self):
        self.ensure_one()
        return self.open_website_url()

    def get_perms(self, category=None):
        _perm_docs_content = document_permission.DocumentPermission()
        _perm_docs_content.load_document_content(self, self.env.user)
        return _perm_docs_content

    def can_view_on_website(self):
        user = self.env.user
        if not self.website_published and not (user.has_group('to_website_docs.group_website_doc_editor') or self.create_uid == user or self.author_id.id == user.partner_id.commercial_partner_id.id):
            return False
        return True

    def get_published(self):
        if self.website_published:
            return 'on'
        return 'off'

    def get_website_url(self):
        self.ensure_one()
        if self.document_id.category_id.document_type == 'hash':
            return '%s#%s' % (self.document_id.category_id.get_website_url(), slug(self.document_id))
        else:
            return '/docs/d/%s/%s' % (slug(self.document_id), str(self.id))

    def _compute_website_url(self):
        for my in self:
            my.website_url = my.get_website_url()

    def _compute_can_publish(self):
        super(WebsiteDocumentContent, self)._compute_can_publish()
        for r in self:
            if r.state == 'approved':
                r.can_publish = True
            else:
                r.can_publish = False

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
                raise UserError(_("You don't have right with this Document Contents '%s' which is published")%(r.document_id.name))
