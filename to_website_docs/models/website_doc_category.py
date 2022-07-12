from odoo import fields, models, api, _
from odoo.tools.translate import html_translate
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError, UserError
from odoo.models import expression
from . import document_permission


class WebsiteDocCategory(models.Model):
    _name = 'website.doc.category'
    _description = 'Website Document Category'
    _inherit = ['mail.thread', 'website.seo.metadata', 'website.published.mixin', 'abstract.website.doc', 'mail.activity.mixin']
    _order = 'sequence, name'
    _perm_docs = None

    name = fields.Char('Name', index=True, required=True, translate=True, tracking=True)
    sequence = fields.Integer('Sequence', default=10, tracking=True)
    description = fields.Text('Description')
    date_published = fields.Date('Published Date', tracking=True)
    image = fields.Char('Image')
    image_cover = fields.Char('Image Cover')
    color_cover = fields.Char('Color Cover')
    css_section = fields.Selection([
        ('col-md-12', '100%'),
        ('col-md-9', '75%'),
        ('col-md-8', '66%'),
        ('col-md-6', '50%'),
        ('col-md-4', '33%'),
        ('col-md-3', '25%')
        ], default='col-md-12')
    css_section_item = fields.Selection([
        ('col-md-12', '100%'),
        ('col-md-6', '50%'),
        ('col-md-4', '33%'),
        ('col-md-3', '25%')
        ], default='col-md-4')

    lang_ids = fields.Many2many('res.lang', 'res_lang_website_doc_category_rel', 'category_id', 'lang_id', string='Languages',
                                help="The languages for which this category applicable. Leave it empty to apply its parent languages."
                                " In case the category has neither language nor parent specified, it will be available to all the available website languages")
    tag_ids = fields.Many2many('website.doc.tag', 'website_doc_tag_website_doc_category_rel', 'category_id', 'tag_id', string='Tags')

    type = fields.Selection([
        ('subject', 'Subject'),
        ('section', 'Section'),
        ('category', 'Category')
        ], 'Type', index=True, required=True, default='category', tracking=True)
    document_type = fields.Selection([
        ('hash', 'Hash'),
        ('link', 'Link')], default='link')
    parent_id = fields.Many2one('website.doc.category', string='Parent', index=True, ondelete='restrict')
    depth = fields.Integer(string='Depth', compute='_compute_depth', store=True, index=True, help="The depth of the category in the category tree."
                         " The root node has zero depth.")
    child_ids = fields.One2many('website.doc.category', 'parent_id', 'Categories')

    child_count = fields.Integer('Child Categories Count', compute='_compute_child_count')
    document_ids = fields.One2many('website.document', 'category_id', string='Documents', help="The documents that belong to this category")
    docs_count = fields.Integer(string='Documents Count', compute='_compute_docs_count')

    public_type = fields.Selection([
        ('100', '100%'),
        ('50', '50%'),
        ('25', '25%'),
        ('0', 'None')], index=True, string="Public Visibility", default="100", tracking=True)
    private_type = fields.Selection([
        ('1', 'Only Me'),
        ('all', 'All Editors'),
        ('user', 'Assigned Editors')], index=True, string="Private Visibility", default="all", tracking=True)

    @api.model
    def _get_default_description_private(self):
        return _("Oops! you don't have permission to access content of this document")

    description_private = fields.Html('Private Description', translate=html_translate, default=_get_default_description_private)

    public_rule_ids = fields.One2many('docs.public.rule', 'category_id', 'Public Rules')
    user_id = fields.Many2one('res.users', 'Responsible', index=True, domain=[('share', '=', False)], tracking=True, help="The internal Editor who"
                              " will have full access rights (incl. to reject/approve) to documents in this category")
    member_ids = fields.Many2many('res.users', 'user_website_doc_category_rel', 'category_id', 'user_id', string='Members',
                                  help="Member of this category can create document inside it")
    has_content = fields.Boolean('Has Content', compute='_get_has_content', help="Technical field to support UI for the right type of category")
    has_approved_doc = fields.Boolean(string='Has Approved Docs', compute='_compute_has_approved_doc', store=True)

    def _find_website(self):
        """
        Find website for displaying
        """
        if self.website_id:
            return self.website_id
        else:
            if self.parent_id:
                return self.parent_id._find_website()
            else:
                return False

    def _compute_child_count(self):
        child_data = self.env['website.doc.category'].read_group([('parent_id', 'in', self.ids)], ['parent_id'], ['parent_id'])
        mapped_data = dict([(child_dict['parent_id'][0], child_dict['parent_id_count']) for child_dict in child_data])
        for r in self:
            r.child_count = mapped_data.get(r.id, 0)

    def _compute_docs_count(self):
        docs_data = self.env['website.document'].sudo().read_group([('category_id', 'in', self.ids)], ['category_id'], ['category_id'])
        mapped_data = dict([(doc['category_id'][0], doc['category_id_count']) for doc in docs_data])
        for r in self:
            r.docs_count = mapped_data.get(r.id, 0)

    @api.depends('document_ids.state')
    def _compute_has_approved_doc(self):
        for r in self:
            if any(doc.state == 'approved' for doc in r.document_ids):
                has_approved_doc = True
            else:
                has_approved_doc = False
            r.has_approved_doc = has_approved_doc

    @api.depends('parent_id', 'parent_id.depth')
    def _compute_depth(self):
        for r in self:
            if r.parent_id:
                r.depth = r.parent_id.depth + 1
            else:
                r.depth = 0

    def _get_has_content(self):
        for r in self:
            r.has_content = r.child_count > 0 or r.docs_count > 0

    def get_image(self):
        return self.image or '/to_website_docs/static/src/img/user.jpg'

    def get_color(self):
        try:
            h = self.color_cover[1:]
            rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2 , 4))
            return 'rgba(%s, 0.3)' % ', '.join(str(x) for x in rgb)
        except:
            return 'rgba(0, 0, 0, 0.3)'

    def get_public_rule(self):
        for rule in self.public_rule_ids:
            if self.env.user in rule.users:
                return rule.public_type
            if self.env.user in rule.groups_id.mapped('users'):
                return rule.public_type
        return self.public_type

    def get_max_index_by_rule(self, documents, public_rule):
        num = len(documents)
        if num == 1:
            return 0
        num = int((public_rule / 100.0) * num)
        if num == 0:
            num = 1
        return num

    def website_publish_button(self):
        result = super(WebsiteDocCategory, self).website_publish_button()
        if self.website_published and not self.date_published:
            self.date_published = fields.Date.today()
        return result

    def action_view_childs(self):
        self.ensure_one()
        res = {}
        # if type == 'subject', children's type will be section
        if self.type == 'subject':
            res = self.env['ir.actions.act_window'].for_xml_id('to_website_docs', 'section_action')
            res['context'] = {'default_type': 'section'}

        # if type == 'section', children's type will be category
        elif self.type == 'section':
            res = self.env['ir.actions.act_window'].for_xml_id('to_website_docs', 'category_action')
            res['context'] = {'default_type': 'category'}

        # @TODO: consider nested cateogries here
        else:
            res = self.env['ir.actions.act_window'].for_xml_id('to_website_docs', 'document_action')
            res['domain'] = [('category_id', '=', self.id)]
            return res

        res['domain'] = [('parent_id', '=', self.id)]
        res['context'].update({'default_parent_id': self.id})
        return res

    def name_get(self):

        def get_names(cat):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    def get_recursive_parents(self):
        """
        Get parents recursively and return category recordset that includes the curent
        
        :return: category recordset sorted in parent -> child -> child of child
        :rtype: website.category recordset
        """
        parent_ids = self.mapped('parent_id')
        if parent_ids:
            recursive_parent_ids = parent_ids.get_recursive_parents()
            return recursive_parent_ids + self
        else:
            return self

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        if (not view_id) and (view_type == 'form'):
            if self.env.context.get('force_section', False):
                view_id = self.env.ref('to_website_docs.section_form').id
        return super(WebsiteDocCategory, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id:
            self.lang_ids = self.parent_id.lang_ids.ids

    def get_applicable_languages(self):
        """
        Recursively search through the parents for languages
        """
        # if the first level category has not language specified, return all available languages
        if not self.parent_id and not self.lang_ids:
            return self.env['res.lang'].search([])

        elif not self.parent_id or self.lang_ids:
            return self.lang_ids
        else:
            return self.parent_id.get_applicable_languages()

    def can_view_on_website(self):
        user = self.env.user
        if not self.website_published and not (user.has_group('to_website_docs.group_website_doc_editor') or self.create_uid == user):
            return False
        return True

    def get_child_for_website(self):
        website_id = self._context.get('website_id', False)
        if not website_id:
            return self.env['website.doc.category']
        else:
            domain = [('parent_id', '=', self.id)] + self.env['website'].browse(website_id)._prepare_docs_categ_domain()
            return self.search(domain)

    def get_website_url(self):
        self.ensure_one()
        if self.type == 'section':
            res = self.parent_id.get_website_url()
        else:
            res = '/docs/c/%s' % slug(self)
        return res

    def _compute_website_url(self):
        for my in self:
            my.website_url = my.get_website_url()

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))
        return True

    def _prepare_documents_domain(self):
        category_id = self.ids;
        if self.type == 'subject':
            category_id = self.child_ids.child_ids.ids
        elif self.type == 'section':
            category_id = self.child_ids.ids
        domain = [('category_id', 'in', category_id)]
        website_id = self.env['website'].browse(self._context.get('website_id', False))
        if website_id:
            domain += website_id._prepare_docs_domain()
        return domain

    def search_document(self):
        """
        Search for all the documents that belong to the current categories (self)
        @rtype: website.document
        """
        domain = self._prepare_documents_domain()
        return self.env['website.document'].search(domain)

    def get_perms(self):
        """
            This is cached after first called
        """
        if self._perm_docs is None:
            self._perm_docs = document_permission.DocumentPermission()
            self._perm_docs.load_category(self, self.env.user)
        return self._perm_docs

    def get_published(self):
        if self.type != 'category' or self.website_published:
            return 'on'
        return 'off'

    def action_publish(self):
        """
        If the context contain `forced_published_date`, it will be used as the date_published instead of the current date
        """
        if not self.env.user.has_group('to_website_docs.group_website_doc_designer'):
            raise ValidationError(_("You must has '%s' access right to publish website document categories.")
                                  % (self.env.ref('to_website_docs.group_website_doc_designer').display_name,))

        # already published once, we will not update the published date anymore
        self.filtered(lambda d: d.website_published == False and d.date_published).write({'website_published': True})
        # set published date for ones that have never been published
        self.filtered(lambda d: d.website_published == False and not d.date_published).write({
            'website_published': True,
            'date_published': self._context.get('forced_published_date', fields.Date.today())
            })
        # publish its parent recursively also. Otherwise it does not make sense when the categories are published inside unpublished categories
        parent_ids = self.mapped('parent_id').filtered(lambda c: not c.website_published)
        if parent_ids:
            parent_ids.action_publish()

    def action_unpublish(self):
        """
        Unpublish the category and their documents
        """
        
        category_published = self.filtered('website_published')
        if category_published:
            if not self.env.user.has_group('to_website_docs.group_website_doc_manager'):
                raise UserError(_("The Documents is published. Only Docs Manager has rights unpublish this document."))
            category_published.write({'website_published': False})
            category_published.document_ids.action_unpublish()
        # unpublish parent if all children unpublish
        parent_id = self.parent_id.filtered('child_ids.website_published') if self.parent_id else False
        if parent_id:
            parent_id.action_unpublish()
        # unpublish their children also
        child_ids = self.child_ids.filtered('website_published')
        if child_ids:
            child_ids.action_unpublish()

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

    def action_recursive_publish(self):
        self.get_recursive_parents().filtered(lambda categ: not categ.website_published).action_publish_toggle()

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

    def unlink(self):
        self.mapped('document_ids').unlink()
        child_ids = self.mapped('child_ids')
        if child_ids:
            child_ids.unlink()
        return super(WebsiteDocCategory, self).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.user.has_group('to_website_docs.group_website_doc_reviewer'):
            for vals in vals_list:
                if not vals.get('user_id', False):
                    vals['user_id'] = self.env.user.id
        return super(WebsiteDocCategory, self).create(vals_list)

    def write(self, vals):
        user = self.env.user
        keys = set(vals.keys())
        check_raise = False
        if not user.has_group('to_website_docs.group_website_doc_manager'):
            for r in self:
                if r.type != 'category':
                    allow_edit = {'image', 'image_cover', 'color_cover', 'css_section', 'css_section_item', 'public_type'}
                    allow_edit_publish = allow_edit | {'website_published', 'is_published', 'date_published'}
                    if user.has_group('to_website_docs.group_website_doc_designer'):
                        if keys - allow_edit_publish:
                            check_raise = True
                    else:
                        if keys - allow_edit:
                            check_raise = True
                    if check_raise:
                        raise UserError(_("You don't have right with this Subject/Section: %s")%(r.name))
        return super(WebsiteDocCategory, self).write(vals)
    