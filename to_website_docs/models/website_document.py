from odoo import fields, models, api, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError, UserError
from odoo.models import expression
from . import document_permission


class WebsiteDocument(models.Model):
    _name = 'website.document'
    _description = 'Website Document'
    _inherit = ['mail.thread', 'website.seo.metadata', 'website.published.mixin', 'abstract.website.doc', 'mail.activity.mixin']
    _order = 'sequence, name'
    _documents = None

    def _user_id_domain(self):
        if self.env.user.has_group('to_website_docs.group_website_doc_reviewer'):
            return []
        return [('id', '=', self.env.user.id)]

    name = fields.Char('Name', index=True, required=True, translate=True, tracking=True)
    sequence = fields.Integer('Sequence', default=10, tracking=True)
    date_published = fields.Date('Published Date', readonly=True, tracking=True, help="Once published, this field will keep unchanged forever")
    tag_ids = fields.Many2many('website.doc.tag', 'website_doc_tag_website_document_rel', 'document_id', 'tag_id', string='Tags')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')], 'Status', default='draft', index=True, copy=False, tracking=True)
    lang_ids = fields.Many2many('res.lang', 'res_lang_website_document_rel', 'document_id', 'lang_id', string='Languages',
                               help="The languages for which this document available. If empty, the language of the corresponding category will be applied.")
    category_id = fields.Many2one('website.doc.category', 'Category', index=True, required=True, ondelete='restrict', tracking=True)
    user_id = fields.Many2one('res.users', 'Assigned to', index=True, default=lambda self: self.env.user, tracking=True, domain=_user_id_domain, copy=False)
    validator_id = fields.Many2one('res.users', 'Validated by', tracking=True)
    content_ids = fields.One2many('website.document.content', 'document_id', 'Contents')
    contents_count = fields.Integer(string='Content Count', compute='_compute_contents_count')
    introtext_length = fields.Integer(string='Intro Text Length', default=400)
    website_id = fields.Many2one(compute='_compute_website', store=True, index=True)
    author_id = fields.Many2one('res.partner', copy=False)

    @api.depends('content_ids')
    def _compute_contents_count(self):
        content_data = self.env['website.document.content'].read_group([('document_id', 'in', self.ids)], ['document_id'], ['document_id'])
        mapped_data = dict([(dict_data['document_id'][0], dict_data['document_id_count']) for dict_data in content_data])
        for r in self:
            r.contents_count = mapped_data.get(r.id, 0)

    def action_view_contents(self):
        content_ids = self.mapped('content_ids')
        action = self.env['ir.actions.act_window']._for_xml_id('to_website_docs.document_content_action')

        # reset context
        action['context'] = {}
        # choose the view_mode accordingly
        total_records = len(content_ids)
        action['context'] = {'default_document_id': self.id}
        if total_records != 1:
            action['domain'] = "[('document_id', 'in', %s)]" % str(self.ids)
        elif total_records == 1:
            res = self.env.ref('to_website_docs.document_content_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = content_ids.id
        return action

    @api.depends('category_id', 'category_id.website_id',
                 'category_id.parent_id', 'category_id.parent_id.website_id')
    def _compute_website(self):
        for r in self:
            r.website_id = r.category_id._find_website()

    def get_applicable_languages(self):
        self.ensure_one()
        return self.lang_ids or self.category_id.get_applicable_languages()

    def _check_lang(self, lang_code='en_US'):
        self.ensure_one()
        if lang_code in self.get_applicable_languages().mapped('code') or self.env.user.has_group('to_website_docs.group_website_doc_editor'):
            return True
        else:
            return False

    def write(self, vals):
        self.with_context(force_write=True)._check_published()
        self._check_role()
        result = super(WebsiteDocument, self).write(vals)
        return result

    def unlink(self):
        self._check_published()
        self._check_role(delete=True)
        content_ids = self.mapped('content_ids')
        if content_ids:
            content_ids.unlink()
        return super(WebsiteDocument, self).unlink()

    def get_website_url(self):
        self.ensure_one()
        if self.category_id.document_type == 'hash':
            return '%s#%s' % (self.category_id.get_website_url(), slug(self))
        else:
            return '/docs/d/%s' % slug(self)

    def _compute_website_url(self):
        for my in self:
            my.website_url = my.get_website_url()

    def action_confirm(self):
        for r in self:
            if r.state not in ('draft', 'rejected'):
                raise UserError(_("You cannot confirm the document %s while its state is not Draft.") % (r.name,))
        self.write({'state': 'confirmed'})

    def action_reject(self):
        if not self.env.user.has_group('to_website_docs.group_website_doc_reviewer'):
            self._raise_documents('to_website_docs.group_website_doc_reviewer')
        for r in self:
            if r.state != 'confirmed':
                raise UserError(_("You cannot reject the document %s while its state is not Confirmed.") % (r.name,))
        self.write({'state': 'rejected'})

    def action_reconfirm(self):
        for r in self:
            if r.state not in ('draft', 'rejected'):
                raise UserError(_("You cannot reconfirm the document %s while its state is neither Draft nor Rejected.") % (r.name,))
        self.write({'state': 'confirmed'})

    def action_approve(self):
        if not self.env.user.has_group('to_website_docs.group_website_doc_reviewer'):
            self._raise_documents('to_website_docs.group_website_doc_reviewer')
        for r in self:
            if r.state not in ('draft', 'confirmed', 'rejected'):
                raise UserError(_("You cannot approve the document %s while its state is neither Draft nor Confirmed nor Rejected.") % (r.name,))
        self.write({
                'validator_id': self.env.user.id,
                'state': 'approved',
                })

    def action_publish(self):
        """
        If the context contain `forced_published_date`, it will be used as the date_published instead of the current date
        """
        if not self.env.user.has_group('to_website_docs.group_website_doc_designer'):
            self._raise_documents('to_website_docs.group_website_doc_designer')
        for r in self:
            if r.state != 'approved':
                raise UserError(_("You cannot publish the document %s while its state is not Approved.") % (r.name,))
            if not r.content_ids.filtered(lambda c: c.website_published == True):
                raise UserError(_("You cannot publish the document %s because not any content is published .") % (r.name,))
        # already published once, we will not update the published date anymore
        self.filtered(lambda d: d.website_published == False and d.date_published).write({'website_published': True})
        # set published date for ones that have never been published
        self.filtered(lambda d: d.website_published == False and not d.date_published).write({
            'website_published': True,
            'date_published': self._context.get('forced_published_date', fields.Date.today())
            })
        # publish its categories recursively also. Otherwise it does not make sense when the document is publish inside a unpublished category
        self.mapped('category_id').filtered(lambda c: not c.website_published).action_publish_toggle()

    def action_cancel(self):
        self.action_unpublish()
        self.write({'state':'cancelled'})

    def action_draft(self):
        if not self.env.user.has_group('to_website_docs.group_website_doc_reviewer'):
            self._raise_documents('to_website_docs.group_website_doc_reviewer')
        for r in self:
            if r.state != 'cancelled':
                raise UserError(_("You cannot set the document %s to Draft while its state is not Cancelled.") % (r.name,))
        self.write({'state': 'draft'})

    def action_unpublish(self):
        documents_published = self.filtered('website_published')
        if documents_published:
            if not self.env.user.has_group('to_website_docs.group_website_doc_manager'):
                raise UserError(_("The Documents is published. Only Docs Manager has rights unpublish this document."))
            documents_published.write({'website_published': False})
            documents_published.content_ids.action_unpublish()
        #unpublish category if all document unpublish
        if not self.category_id.filtered_domain([('document_ids.website_published', '=', True)]):
            self.category_id.action_unpublish()

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
        result = super(WebsiteDocument, self).website_publish_button()
        self.action_publish_toggle()
        return result

    def get_perms(self, category=None):
        _perm_docs = document_permission.DocumentPermission()
        _perm_docs.load_document(self, self.env.user)
        return _perm_docs

    def _prepare_prefetch_fields(self):
        return ['name', 'state', 'website_published', 'website_url', 'content_ids']

    def _prepare_content_domain(self):
        return [('document_id', 'in', self.ids)]

    def get_content(self):
        """
        @rtype: website.document.content
        """
        domain = self._prepare_content_domain()

        content_id = self.env['website.document.content'].search(domain, limit=1)
        return content_id

    def get_content_index(self):
        content_id = self.get_content()
        childs = []
        if content_id:
            childs = content_id._generate_indexes_from_h_tags()
        return childs

    def can_view_on_website(self):
        user = self.env.user
        if not self.website_published and not (user.has_group('to_website_docs.group_website_doc_editor') or self.create_uid == user or self.author_id.id == user.partner_id.commercial_partner_id.id):
            return False
        return True

    def get_published(self):
        if self.website_published:
            return 'on'
        return 'off'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            for s in name.split(' '):
                s = s.strip()
                if len(s) > 0:
                    domain += [('name', 'ilike', s)]

            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        return self.search(domain + args, limit=limit).name_get()

    @api.model
    def _validate_merge(self, dest_document):
        if self == dest_document:
            raise ValidationError(_("You cannot merge two same documents"))

    def _get_merge_fields_data(self):
        """
        For potential inheritance
        """
        vals = {}
        if self._context.get('update_dest_doc_name', False):
            vals['name'] = self.name
        if self.lang_ids:
            vals['lang_ids'] = [(4, lang_id) for lang_id in self.lang_ids.ids]
        if self.tag_ids:
            vals['tag_ids'] = [(4, tag_id) for tag_id in self.tag_ids.ids]
        return vals

    @api.model
    def merge(self, dest_document):
        """
        This method merge the current document with the given destination document
        @param dest_document: The destination document into which the current document will be merged

        @return: the recordset of the contents of the current document which have been merged into the destination document
        @rtype: website.document.content
        """
        self._validate_merge(dest_document)
        content_ids = self.content_ids
        self.content_ids.write({
            'document_id': dest_document.id
            })
        dest_doc_update_data = self._get_merge_fields_data()
        if bool(dest_doc_update_data):
            dest_document.write(dest_doc_update_data)
        self.unlink()
        return content_ids

    def _compute_can_publish(self):
        for r in self:
            if r.state == 'approved':
                r.can_publish = True
            else:
                r.can_publish = False

    def _raise_documents(self, group_id):
        raise UserError(_("You must has '%s' access right for this action on website documents/Contents.")
                                  % (self.env.ref('%s'%group_id).display_name,))

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
                raise UserError(_("You don't have right with this Document %s which is published")%r.name)

    def _check_role(self,delete=False):
        for r in self:
            user = self.env.user
            if not user.has_group("to_website_docs.group_website_doc_manager"):
                author = r.author_id.user_ids.filtered(lambda u:u.company_id == self.env.company)
                # design
                if user.has_group("to_website_docs.group_website_doc_designer"):
                    if r.user_id.has_group("to_website_docs.group_website_doc_designer"):
                        # check delete
                        if delete and not user == author and author.has_group("to_website_docs.group_website_doc_designer"):
                            self._raise_delete(r.name)
                        # check edit
                        if r.user_id and user != r.user_id:
                            if delete:
                                self._raise_delete(r.name)
                            self._raise_edit(r.name)
                    else: #  check delete with document assigned for the subordinate user
                        if delete and not user == author and author.has_group("to_website_docs.group_website_doc_designer"):
                            self._raise_delete(r.name)

                # reviewer
                elif user.has_group("to_website_docs.group_website_doc_reviewer"):
                    if r.user_id.has_group("to_website_docs.group_website_doc_reviewer"):
                        # check delete
                        if delete and not user == author and author.has_group("to_website_docs.group_website_doc_reviewer"):
                            self._raise_delete(r.name)
                        # check edit
                        if r.user_id and user != r.user_id:
                            if delete:
                                self._raise_delete(r.name)
                            self._raise_edit(r.name)
                    else: #  check delete with document assigned for the subordinate user
                        if delete and not user == author and author.has_group("to_website_docs.group_website_doc_reviewer"):
                            self._raise_delete(r.name)

    def _raise_delete(self, name):
        raise UserError(_("You cannot delete documents/contents created by others: '%s'")%(name))

    def _raise_edit(self, name):
        raise UserError(_("You cannot edit documents/contents assigned to others: '%s'")%(name))
