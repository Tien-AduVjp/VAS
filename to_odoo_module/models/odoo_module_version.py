import logging
import os
import lxml.html

from werkzeug import urls
from werkzeug.urls import url_encode
from psycopg2.extensions import AsIs

from odoo import models, fields, api, tools, _
from odoo.tools.translate import html_translate
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import ValidationError

from .git_branch import downgrade_heading

_logger = logging.getLogger(__name__)


class OdooModuleVersion(models.Model):
    _name = 'odoo.module.version'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'rotating.token.mixin', 'image.mixin']
    _order = 'full_version_str desc'
    _description = 'Odoo Module Version'
    _mail_post_access = 'read'

    name = fields.Char(string='Name', translate=True, required=True, index=True)
    sequence = fields.Integer(string='Sequence', default=10)

    icon = fields.Image(string="Module Version Icon", attachment=True, max_width=64, max_height=64,
                             help="Image here will be resized as a 64x64px image automatically. If this module is fetched from a Git Branch,"
                             " the image static/description/img/icon.png will be filled here")
    image_1920 = fields.Image(string="Main Screenshot", attachment=True)

    zipped_source_code = fields.Binary(string='Zipped Source Code', attachment=True,
                                       groups="to_odoo_module.odoo_module_user",
                                       help="The source code of the Odoo Module version in zip archive. If you have a git branch, you do NOT need to upload your module here")
    filename = fields.Char(string='File Name', compute='_compute_file_name', help="Technical field for forming the file name of the Zipped Source Code")
    zip_all_filename = fields.Char(string='All Zipped File Name', compute='_compute_file_name', help="Technical field for forming the file name of the All Zipped")
    version = fields.Char(string='Version', required=True, tracking=True,
                          help="The version of the module, which is also declared in the module's __manifest__.py")
    module_id = fields.Many2one('odoo.module', string='Odoo Module', required=True, tracking=True, ondelete="cascade", auto_join=True, index=True)
    product_id = fields.Many2one('product.product', string='Product', index=True, auto_join=True,
                                 help="Product for which this module version presents for accounting integration."
                                 " Do not fill it if you don't sell this module (e.g. an Odoo standard module)")
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', related='product_id.product_tmpl_id', store=True, index=True)
    technical_name = fields.Char(string='Technical Name', required=True, index=True, tracking=True)
    source_path = fields.Char(string='Source Path', compute='_compute_path', help="Path to source code fetched by Git")
    old_technical_name = fields.Char(string='Old Technical Name', help="Please specify the old technical name if this version's has changed."
                                     " Please also make sure that the key 'old_technical_name' in the manifest file of the module source"
                                     " code has its proper value.")
    odoo_version_id = fields.Many2one('odoo.version', string='Odoo Version', required=True, index=True, tracking=True)
    full_version_str = fields.Char(string='Full Version', compute='_compute_full_version_str', store=True, index=True,
                                   help="Full version which is computed by concatenating the Odoo Version and the Version")
    summary = fields.Text(string='Summary', translate=True)
    description = fields.Text(string='Rst. Description', translate=True, help="This field stores the content of the description"
                              " key in the manifest file of the module and will be updated automatically each time the"
                              " corresponding is discovered for Odoo modules")
    doc_rst = fields.Text(string='Rst. Doc', translate=True, help="This field stores the content of the document file (if exists"
                          " in the module's doc/index.rst. This will be updated automatically each time the corresponding is"
                          " discovered for Odoo modules")
    index_html = fields.Html(string='HTML Description', translate=html_translate, sanitize_attributes=False, readonly=True,
                             help="This field stores the content of the index.html"
                             " which is stored at the module's 'static/description/index.html' and will be updated automatically each time"
                             " the corresponding is discovered for Odoo modules.")
    description_html = fields.Html('Description HTML', compute='_get_desc', translate=html_translate)
    authors = fields.Char(string='Authors List', help="Technical field that store list of authors fetched from Git", readonly=True)
    author_ids = fields.Many2many('software.author', 'software_author_odoo_module_version_rel', 'module_version_id', 'author_id', string='Authors',
                                  help="The author(s) of this module version")
    website = fields.Char(string='Author Website')
    live_test_url = fields.Char(string='Live Demo', translate=True)
    support = fields.Char(string='Support', help="support email / url")
    depends = fields.Char(string='Depends', readonly=True, help="List of depending modules (name's comma separator) on which this module depends")
    depending_module_version_ids = fields.Many2many('odoo.module.version', 'odoo_module_version_dependencies', 'module_file_id', 'dependent_module_file_id',
                                            string='Dependencies', help="List of modules on which this module directly depends. The list will be generated"
                                            " based on the values of the Depends field upon create/update")
    depended_module_version_ids = fields.Many2many('odoo.module.version', 'odoo_module_version_dependencies', 'dependent_module_file_id', 'module_file_id',
                                            string='Inheritances', help="List of modules that directly depends on this module")
    recursive_depending_module_version_ids = fields.Many2many('odoo.module.version',
                                                      compute='_compute_recursive_depending_module_versions',
                                                      string='Recursive Dependencies',
                                                      help="List of module versions on which this module version recursively depends")
    included_dependency_ids = fields.Many2many('odoo.module.version',
                                                      compute='_compute_recursive_depending_module_versions',
                                                      string='Required None Standard Apps',
                                                      help="List of None Odoo's standard Applications on which this depends")
    required_standard_odoo_app_ids = fields.Many2many('odoo.module.version',
                                                      compute='_compute_recursive_depending_module_versions',
                                                      string='Required Standard Apps',
                                                      help="List of Odoo's standard Applications on which this depends")

    ee_required = fields.Boolean(string='EE Required', compute='_compute_ee_required', store=True, help="This field is to indicate if"
                               " the module version requires Odoo Enterprise Edition")
    recursive_depended_module_version_ids = fields.Many2many('odoo.module.version',
                                                             compute='_compute_recursive_depended_module_versions',
                                                             string='Recursive Inheritances',
                                                             help="List of module versions that depends on this module version recursively")
    installable = fields.Boolean(string='Installable', tracking=True)
    application = fields.Boolean(string='Application', tracking=True)
    auto_install = fields.Boolean(string='Auto-install', tracking=True)
    price_currency = fields.Monetary(string='Currency Price', tracking=True, currency_field='currency_id',
                                     help="The original price (in the Currency specified below) that is input by either the user or being fetch from the git repository.")
    recursive_price_currency = fields.Monetary(string='Recursive Currency Price', currency_field='currency_id', compute='_compute_recursive_currency_price',
                                               help="The total currency price of the module version including its recursive dependencies' price")
    currency_id = fields.Many2one('res.currency', string='Currency', tracking=True,
                                  default=lambda self: self.env.company.currency_id,
                                  required=True, help="The original currency that is input by either the user or being fetch from the git repository.")
    price = fields.Monetary(string='Price', currency_field='company_currency_id', compute='_compute_price',
                            help="The price that is converted to the company's currency")
    recursive_price = fields.Monetary(string='Recursive Price', currency_field='company_currency_id', compute='_compute_recursive_price',
                            help="The total price of the module version including its recursive dependencies' price")
    company_currency_id = fields.Many2one('res.currency', string='Company Currency', compute='_compute_company_currency')
    license_version_id = fields.Many2one('product.license.version', string='License Version', tracking=True)
    license_id = fields.Many2one('product.license', related='license_version_id.license_id', store=True, tracking=True)
    git_branch_id = fields.Many2one('git.branch', string='Git Branch', tracking=True, index=True,
                                    help="The git branch that controls the source code of this Odoo module version")
    git_repository_id = fields.Many2one('git.repository', related='git_branch_id.repository_id', store=True, index=True, readonly=True)
    is_standard_enterprise_module = fields.Boolean(string='Standard Enterprise Module', compute='_compute_is_standard_enterprise_module', store=True,
                                                   help="This field is to indicate if the module version is a standard Odoo module"
                                                   " that is delivered in Odoo Enterprise source base.")
    is_standard_odoo_module = fields.Boolean(string='Standard Odoo Module', compute='_compute_is_standard_odoo_module', store=True,
                                             help="This field is to indicate if the module version is a standard Odoo module"
                                             " that is delivered in Odoo source base.")

    ir_module_category_id = fields.Many2one('ir.module.category', tracking=True, string='Category')
    other_version_ids = fields.Many2many('odoo.module.version', string='Other Versions', compute='_compute_other_versions',
                                         help="List of the Odoo Module Versions of the same Odoo Module")
    is_latest_version = fields.Boolean(string='Is the latest version', compute='_compute_is_latest_version', store=True)
    image_ids = fields.One2many('odoo.module.version.image', 'module_version_id', string='Images')
    company_id = fields.Many2one(related='git_branch_id.company_id', store=True, index=True, readonly=True, help="The company to which the"
                                " module version belong.")
    vendor_id = fields.Many2one(related='git_branch_id.vendor_id', store=True, index=True,
                                help="The partner who holds the copyright of this Odoo Module Version")
    by_third_party = fields.Boolean(string='By Third Party', compute='_compute_by_third_party')
    download_stat_ids = fields.One2many('odoo.module.version.download.stat', 'odoo_module_version_id', string='Download Log')
    external_downloads_count = fields.Integer(string='Total External Downloads', compute='_compute_external_downloads_count', store=True, index=True)
    total_downloads_count = fields.Integer(string='Total Downloads', compute='_compute_downloads_count')
    can_download = fields.Boolean(string='Can Download', compute='_compute_can_download', help="Technical field to indicate if this module version is"
                                  " downloadable by the current external user. This has no affect on internal users")
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the odoo module version without removing it.")

    _sql_constraints = [
        ('check_price_currency_nagative',
         'CHECK(price_currency >= 0.0)',
         "Negative Currency Price makes no sense!"),
    ]

    def _get_manifest_description_keys(self):
        return [
            'summary',
            'description'
            ]

    def toggle_active(self):
        super(OdooModuleVersion, self).toggle_active()
        modules = self.mapped('module_id').with_context(ignore_toggle_versions=True)
        modules.filtered(lambda m: all(not version.active for version in m.odoo_module_version_ids) and m.active).toggle_active()
        modules.filtered(lambda m: any(version.active for version in m.odoo_module_version_ids) and not m.active).toggle_active()
        self.mapped('product_id').filtered(lambda p: p.active != p.odoo_module_version_id.active).toggle_active()

    @api.depends('version', 'module_id', 'odoo_version_id')
    def _check_unique_version_per_odoo_version_per_module(self):
        OdooModuleVersion = self.env['odoo.module.version']
        for r in self:
            overlap = OdooModuleVersion.search([
                ('id', '!=', r.id),
                ('module_id', '=', r.module_id.id),
                ('odoo_version_id', '!=', r.odoo_version_id.id)], limit=1)
            if overlap:
                raise ValidationError(_("You must not have more than one Odoo module version of the same Odoo module and Odoo version"
                                        ". In other words, the Odoo module version '%s' has the same Odoo module and Odoo version as"
                                        " the existing Odoo module version %s's")
                                        % (r.display_name, overlap.display_name))
            overlap = OdooModuleVersion.search([
                ('id', '!=', r.id),
                ('version', '=', r.version),
                ('module_id', '=', r.module_id.id),
                ('odoo_version_id', '!=', r.odoo_version_id.id)], limit=1)
            if overlap:
                raise ValidationError(_("You were trying to create a module version named '%s' that has the same version %s and"
                                        " Odoo version %s and of the same module %s as the existing one %s's")
                                        % (r.display_name, r.version, r.odoo_version_id.name, r.module_id.name, overlap.display_name))

    def _get_token_lifetime(self):
        if self.company_id.dedicated_app_download_token_lifetime:
            if float_compare(self.company_id.app_download_token_lifetime, 0.0, precision_digits=2) == 1:
                return self.company_id.app_download_token_lifetime
            else:
                return False
        else:
            return super(OdooModuleVersion, self)._get_token_lifetime()

    def action_get_download_url(self):
        local_context = dict(
            self.env.context,
            default_model='odoo.module.version',
            default_odoo_module_version_id=self.id,
        )
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.odoo.module.version.public.download',
            'target': 'new',
            'context': local_context,
            }

    def get_download_url(self):
        base_url = '/' if self.env.context.get('relative_url') else \
                   self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.ensure_one()
        # do not rotate token if self.id is an instance of NewId
        # as this method is also called on onchange in views, regenerate token may cause form data lost
        # in such case, we provide context to control whether or not ensuring rotating token
        if not isinstance(self.id, models.NewId) and not self._context.get('do_not_ensure_rotating_token', False):
            self._ensure_rotating_token()
        params = {
            'access_token': self.access_token,
            }

        if hasattr(self, 'partner_id') and self.partner_id:
            params.update(self.partner_id.signup_get_auth_param()[self.partner_id.id])

        return urls.url_join(base_url, '/my/apps/download/%s?%s' % (self.id, url_encode(params)))

    def _compute_by_third_party(self):
        for r in self:
            r.by_third_party = r.vendor_id and r.vendor_id.commercial_partner_id != r.company_id.partner_id.commercial_partner_id

    def _compute_can_download(self):
        partner = self._context.get('partner', self.env.user.partner_id)
        user_paid_apps = partner.get_paid_odoo_apps()[0]
        for r in self:
            can_download = True
            for module_version in self.sudo().get_recursive_dependencies(incl_the_current=True):
                if (not module_version.currency_id.is_zero(module_version.price_currency) and module_version not in user_paid_apps) \
                        or all([user.has_group('base.group_public') for user in partner.user_ids]):
                    can_download = False
                    break
            r.can_download = can_download

    @api.depends('git_branch_id.is_odoo_enterprise_source_code')
    def _compute_is_standard_enterprise_module(self):
        for r in self:
            r.is_standard_enterprise_module = r.git_branch_id.is_odoo_enterprise_source_code

    @api.depends('git_branch_id.is_odoo_source_code', 'git_branch_id.is_odoo_enterprise_source_code')
    def _compute_is_standard_odoo_module(self):
        for r in self:
            r.is_standard_odoo_module = r.git_branch_id.is_odoo_source_code or r.git_branch_id.is_odoo_enterprise_source_code

    @api.depends('download_stat_ids', 'download_stat_ids.by_internal_user')
    def _compute_external_downloads_count(self):
        domain = [('odoo_module_version_id', 'in', self.ids), ('by_internal_user', '=', False)]
        download_stat_data = self.env['odoo.module.version.download.stat'].read_group(
            domain,
            ['odoo_module_version_id'],
            ['odoo_module_version_id'])
        mapped_data = dict([(download_stat['odoo_module_version_id'][0], download_stat['odoo_module_version_id_count']) for download_stat in download_stat_data])
        for r in self:
            r.external_downloads_count = mapped_data.get(r.id, 0)

    def _compute_downloads_count(self):
        domain = [('odoo_module_version_id', 'in', self.ids)]
        filtered_user = self._context.get('filtered_user', False)
        if filtered_user:
            domain.append(('user_id', '=', filtered_user.id))

        download_stat_data = self.env['odoo.module.version.download.stat'].read_group(
            domain,
            ['odoo_module_version_id'],
            ['odoo_module_version_id'])
        mapped_data = dict([(download_stat['odoo_module_version_id'][0], download_stat['odoo_module_version_id_count']) for download_stat in download_stat_data])
        for r in self:
            r.total_downloads_count = mapped_data.get(r.id, 0)

    def _sorted_by_full_version_str(self, reverse=False):
        """
        Sort records in self by their full_version_str in ascending (or descending, if the given reverse is True) order
        """
        return self.sorted(
            # Hint: This lambda function will return a list like [12, 0, 6, 2, 1] presenting '12.0.6.2.1'."
            # Any non-digit will be converted to 0.
            # For example, '12.0.6.2.beta' will become '12.0.6.2.0'
            key=lambda v: list(
                map(
                    int,
                    [x if x.isdigit() else '0' for x in (v.full_version_str or '').split('.')]
                    )
                ),
            reverse=reverse
            )

    def _prepare_download_stat_data(self, user, free_download=None):
        """
        @param user: the user who did the download. We cannot use self.env.user since this is usually called by sudo()
        @type user: res.users
        @param free_download: to mark if this is a free download. If not passed, the value will be calculated based on the module price
        @type free_download: bool

        @return: data to create a new odoo.module.version.download.stat record
        @rtype: dict
        """
        if free_download is None:
            if float_compare(self.price_currency, 0.0, precision_rounding=self.currency_id.rounding) == 1:
                free_download = False
            else:
                free_download = True
        return {
            'odoo_module_version_id': self.id,
            'user_id': user.id,
            'by_internal_user': user.share == False,
            'free_download': free_download,
            }

    def increase_download_count(self, free_download=None):
        # This method could be called somewhere with sudo() and pass download_user into the context
        user = self._context.get('download_user', self.env.user)
        vals_list = [r._prepare_download_stat_data(user, free_download) for r in self]
        return self.env['odoo.module.version.download.stat'].create(vals_list)

    def _compute_path(self):
        # working_tree if git.branch is a none-store computed field
        # read all at once for better performance (avoiding compute working_tree of the same branch again and again)
        working_trees = self.mapped('git_branch_id').read(['working_tree'])
        mapped_data = dict([(it['id'], it['working_tree']) for it in working_trees])
        for r in self:
            r.source_path = os.path.join(mapped_data.get(r.git_branch_id.id), r.technical_name) if r.git_branch_id else False

    def read_resource(self, resource_name, path='static/description'):
        """
        @param resource_name: the name of the resource (e.g. screen_shot.png) which is stored at the path
        @param path: the relative path to the module's source_path that stores the resource

        @return: the content of the resource in bytes
        @rtype: bytes
        """
        resource_path = os.path.join(self.source_path, path, resource_name)
        resource_path = os.path.normpath(resource_path)
        if os.path.isfile(resource_path):
            with open(resource_path, 'rb') as res:
                return res.read()
        return False

    def _get_description_data(self):
        Branch = self.env['git.branch']

        def parse_rst(rst):
            html_str = Branch.rst2html(rst)
            html = lxml.html.fromstring(html_str)
            html = downgrade_heading(html)
            return lxml.html.tostring(html, encoding='unicode')

        mapped_data = {}
        # ensure we have records in self. Otherwise, self.read() will fail
        if self._origin:
            descriptions = self._origin.read(['index_html', 'description'])
            mapped_data = dict([(it['id'], it['index_html'] or parse_rst(it['description'])) for it in descriptions])
        elif self:
            mapped_data = dict([(r.id, r.index_html or parse_rst(r.description)) for r in self])
        return mapped_data

    @api.depends('index_html', 'description')
    def _get_desc(self):
        mapped_data = self._get_description_data()
        for r in self:
            r.description_html = mapped_data.get(r.id, '')

    @api.onchange('git_branch_id')
    def _onchange_git_branch(self):
        if self.git_branch_id:
            self.file = False
            if self.git_branch_id.vendor_id:
                self.vendor_id = self.git_branch_id.vendor_id

    @api.depends('depending_module_version_ids', 'depending_module_version_ids.is_standard_enterprise_module', 'is_standard_enterprise_module')
    def _compute_ee_required(self):
        for r in self:
            ee_module_versions = r.get_recursive_dependencies().filtered(lambda mv: mv.is_standard_enterprise_module)
            r.ee_required = r.is_standard_enterprise_module or True if ee_module_versions else False

    def _compute_file_name(self):
        for r in self:
            r.update({
                'filename': "{0}-v{1}-Odoo_v{2}.zip".format(r.technical_name, r.version, r.odoo_version_id.name),
                'zip_all_filename': "{0}-v{1}_all-Odoo_v{2}.zip".format(r.technical_name, r.version, r.odoo_version_id.name),
                })

    def get_company(self):
        return self.git_branch_id.company_id or self.env.company

    def _compute_company_currency(self):
        """
        Company currency is either the corresponding branch company's currency (if a company is specified)
        or the current user's company's currency (if no company is specified for the branch)
        """
        for r in self:
            r.company_currency_id = r.get_company().currency_id

    def _get_price(self):
        """
        Get the Odoo module version's price in company's currency
        """
        if float_is_zero(self.price_currency, precision_rounding=self.currency_id.rounding):
            return 0.0
        else:
            return self.currency_id._convert(self.price_currency, self.company_currency_id, self.get_company(), fields.Date.today())

    def _compute_price(self):
        """
        Compute price in company's currency
        """
        for r in self:
            r.price = r._get_price()

    def _compute_recursive_currency_price(self):
        for r in self:
            odoo_module_versions = r.get_recursive_dependencies(incl_the_current=True)
            if odoo_module_versions:
                r.recursive_price_currency = sum(odoo_module_versions.mapped('price_currency'))
            else:
                r.recursive_price_currency = 0.0

    def _compute_recursive_price(self):
        for r in self:
            if float_is_zero(r.recursive_price_currency, precision_rounding=r.currency_id.rounding):
                r.recursive_price = 0.0
            else:
                r.recursive_price = r.currency_id._convert(r.recursive_price_currency, r.company_currency_id, r.get_company(), fields.Date.today())

    def _get_query_for_other_versions(self):
        sql = """
            WITH tmp AS (
                SELECT module_id, array_agg(id) AS ids
                FROM %s
                WHERE module_id IN %s
                GROUP BY module_id
            )
            SELECT a.id, array_remove(tmp.ids, a.id)
            FROM %s AS a
            JOIN tmp ON tmp.module_id = a.module_id
            WHERE a.id IN %s
        """
        if self._context.get('exclude_standard_odoo_ee_module'):
            sql += """
                AND a.is_standard_enterprise_module = False
                """
        if self._context.get('exclude_standard_odoo_ce_module'):
            sql += """
                AND a.is_standard_odoo_module = False
                """
        return sql

    def _compute_other_versions(self):
        odoo_modules = self.mapped('module_id')
        if odoo_modules:
            # This does bypass ORM but it would be safe to use.
            self.env.cr.execute(
                self._get_query_for_other_versions(),
                (AsIs(self._table),
                 tuple(odoo_modules.ids),
                 AsIs(self._table),
                 tuple(self.ids))
                )
            res = self.env.cr.fetchall()
            mapped_dict = dict(res)
            for r in self:
                r.other_version_ids = [(6, 0, mapped_dict.get(r.id, []))]
        else:
            for r in self:
                r.other_version_ids = False

    @api.depends('module_id', 'module_id.odoo_module_version_id')
    def _compute_is_latest_version(self):
        for r in self:
            r.is_latest_version = True if r.module_id.odoo_module_version_id == r else False

    def generate_dependencies(self):
        """
        This method generates/updates direct dependencies for the current module.
        """
        related_odoo_module_versions = self.env['odoo.module.version'].with_context(active_test=False).search([
            ('odoo_version_id', 'in', self.mapped('odoo_version_id').ids)])
        for r in self:
            cmd = []
            if r.depends:
                module_names = [name for name in r.depends.split(',') if name]
                odoo_module_versions = related_odoo_module_versions.filtered(
                    lambda omv: omv.technical_name in module_names \
                    and omv.odoo_version_id == r.odoo_version_id \
                    # we don't want the module to depend on a module in another branch of the same repository
                    # in other words, the dependency must in either a different repo or the same branch
                    and (omv.git_repository_id != r.git_repository_id or omv.git_branch_id == r.git_branch_id)
                    )
                if r.git_repository_id.exclude_dependencies_from_repo_ids:
                    odoo_module_versions.filtered(
                        lambda omv: omv.git_repository_id not in r.git_repository_id.exclude_dependencies_from_repo_ids
                        )
                # replace relations
                cmd += [(6, 0, odoo_module_versions.ids)]
            elif r.depending_module_version_ids:
                # remove existing relation
                cmd += [(3, module_version.id) for module_version in r.depending_module_version_ids]

            if cmd:
                r.depending_module_version_ids = cmd

    def make_zip(self):
        """
        This zip all the module in self and return bytes which is ready for storing in Binary fields

        @return: return bytes object containing data for storing in Binary fields
        @rtype: bytes
        """
        source_paths = self.mapped('source_path')
        if source_paths:
            return self.env['git.branch'].zip_dirs(source_paths)
        return False

    def generate_authors(self):

        def smart_map_partner(author_name):
            Partner = self.env['res.partner'].sudo()
            partner_id = Partner.search([('name', '=', author_name)], limit=1)
            if not partner_id:
                partner_id = Partner.search([('name', 'like', author_name)], limit=1)
            if not partner_id:
                partner_id = Partner.search([('name', 'ilike', author_name)], limit=1)
            return partner_id

        SoftwareAuthor = self.env['software.author']
        # for use in a context where user has no create permission
        if self._context.get('use_sudo', False):
            SoftwareAuthor = SoftwareAuthor.sudo()

        for r in self:
            update_data = {}
            if r.authors:
                author_names = [author.strip() for author in r.authors.split(',') if author]
                author_ids = self.env['software.author']
                for author_name in author_names:
                    author_id = SoftwareAuthor.search([('name', '=', author_name)], limit=1)
                    if not author_id:
                        data = {'name': author_name}
                        partner_id = smart_map_partner(author_name)
                        if partner_id:
                            data['partner_id'] = partner_id.id
                        author_id = SoftwareAuthor.create(data)
                    if author_id:
                        author_ids |= author_id
                if author_ids:
                    # replace relations
                    update_data['author_ids'] = [(6, 0, author_ids.ids)]
            elif r.author_ids:
                # remove existing relation
                update_data['author_ids'] = [(3, author_id) for author_id in r.author_ids.ids]

            if bool(update_data):
                r.write(update_data)

    def get_recursive_dependencies(self, incl_the_current=False):
        """
        :param incl_the_current: if True, the result will including self. It will be useful for download modules it their dependencies

        :return: Odoo Module Version records that are children of self recursively. If incl_the_current is passed with True, the result will including self
        :rtype: odoo.module.version
        """
        depending_module_versions = self.mapped('depending_module_version_ids')

        exclude_standard_odoo_modules = self._context.get('exclude_standard_odoo_modules', False)
        if exclude_standard_odoo_modules:
            depending_module_versions = depending_module_versions.filtered(lambda m: not m.is_standard_odoo_module)

        for module_version in depending_module_versions:
            depending_module_versions |= module_version.get_recursive_dependencies(incl_the_current=False)

        if incl_the_current:
            depending_module_versions |= self
        return depending_module_versions

    def get_unbought_recursive_dependencies(self, incl_the_current=False):
        """
        Get the partner's unbought dependencies of the self

        :param incl_the_current: indicate if the return result should include self or not

        :return: recordset of odoo.module.version containing module versions that have not been bought by the partner
        :rtype: odoo.module.version recordset
        """
        partner = self._context.get('partner', self.env.user.partner_id)
        dependencies = self.with_context(exclude_standard_odoo_modules=True).get_recursive_dependencies(incl_the_current=incl_the_current)
        # already bought before
        already_bought = partner.get_paid_odoo_apps(use_commercial_partner=True)[0]

        # find dependencies that were bought before by intersecting the dependencies and the already_bought
        bought_dendencies = dependencies & already_bought

        unbought = dependencies - bought_dendencies
        return unbought

    def _compute_recursive_depending_module_versions(self):
        """
        compute for the list of module versions on which this current module version depends
        """
        for r in self:
            module_versions = r.get_recursive_dependencies(incl_the_current=False)
            r.recursive_depending_module_version_ids = module_versions
            r.included_dependency_ids = module_versions.filtered(lambda mv: not mv.is_standard_odoo_module)
            r.required_standard_odoo_app_ids = module_versions.filtered(lambda mv: mv.is_standard_odoo_module and mv.application)

    def get_recursive_inheritances(self):
        module_versions = self.mapped('depended_module_version_ids')
        for module_version in module_versions:
            module_versions |= module_version.get_recursive_inheritances()
        return module_versions

    def _compute_recursive_depended_module_versions(self):
        """
        compute for the list of module versions that depends on this current module version
        """
        for r in self:
            module_versions = r.get_recursive_inheritances()
            r.recursive_depended_module_version_ids = module_versions

    def get_top_level_module_versions(self):
        """
        Get the top level module versions in the dependencies tree of the self.
        In other words, this will exclude all the module versions that has one in self depending on them
        """
        modules_and_dependencies = self.get_recursive_dependencies(incl_the_current=True)
        res = self.env['odoo.module.version']
        for r in self:
            recursive_inheritances = r.get_recursive_inheritances()
            if all(inheritance not in modules_and_dependencies for inheritance in recursive_inheritances):
                res += r
        return res

    @api.depends('version', 'odoo_version_id.name')
    def _compute_full_version_str(self):
        for r in self:
            items = []
            if r.odoo_version_id.name:
                items.append(r.odoo_version_id.name)
            if r.version:
                if r.odoo_version_id and len(r.version) >= 8 and r.version[:len(r.odoo_version_id.name)] == r.odoo_version_id.name and r.version[len(r.odoo_version_id.name)] == '.':
                    items.append(r.version[len(r.odoo_version_id.name) + 1:])
                else:
                    items.append(r.version)
            r.full_version_str = ".".join(items) if items else False

    @api.onchange('module_id')
    def _onchange_module_id(self):
        if self.module_id:
            description = False
            technical_name = False
            if self.module_id.description:
                description = self.module_id.description
            if self.module_id.technical_name:
                technical_name = self.module_id.technical_name

            self.update({
                'description': description,
                'technical_name': technical_name,
                })

    def name_get(self):
        result = []
        for r in self:
            if r.vendor_id:
                # since this may get accessed by portal/public users, we apply sudo here to avoid
                # permission error when reading vendor's name
                result.append((r.id, _("%s [%s] By %s") % (r.module_id.name, r.full_version_str, r.sudo().vendor_id.name)))
            else:
                result.append((r.id, '%s [%s]' % (r.module_id.name, r.full_version_str)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|',
                        ('module_id.name', 'ilike', '%' + name + '%'),
                        ('full_version_str', 'ilike', '%' + name + '%'),
                        ('module_id.name', operator, name)
                        ]
        files = self.search(domain + args, limit=limit)
        return files.name_get()

    def _create_odoo_module_if_not_exists(self):
        OdooModule = self.env['odoo.module']
        OdooVersion = self.env['odoo.version']

        name = self._context.get('name', '')
        if not name:
            raise ValidationError(_("Programming Error! No Name is passed into the context for the method `_create_odoo_module_if_not_exists()`"))

        technical_name = self._context.get('technical_name', '')
        if not technical_name:
            raise ValidationError(_("Programming Error! No Technical Name is passed into the context for the method `_create_odoo_module_if_not_exists()`"))

        old_technical_name = self._context.get('old_technical_name', '')

        odoo_version = self._context.get('odoo_version_id', False)
        if not odoo_version:
            raise ValidationError(_("Programming Error! No Odoo Version is passed into the context for the method `_create_odoo_module_if_not_exists()`"))
        if isinstance(odoo_version, int):
            odoo_version = OdooVersion.browse(odoo_version)

        git_branch = self._context.get('git_branch_id', False)
        if not git_branch:
            raise ValidationError(_("Programming Error! No Git Branch is passed into the context for the method `_create_odoo_module_if_not_exists()`"))
        if isinstance(git_branch, int):
            git_branch = self.env['git.branch'].browse(git_branch)

        # search for existing odoo module
        odoo_module = OdooModule.with_context(active_test=False).search([
            ('odoo_module_version_ids.technical_name', '=', technical_name),
            ('git_repository_id', '=', git_branch.repository_id.id)
            ], limit=1)
        if not odoo_module:
            odoo_module = OdooModule.with_context(active_test=False).search([
                ('technical_name', '=', technical_name),
                ('git_repository_id', '=', git_branch.repository_id.id)
                ], limit=1)
        if not odoo_module and old_technical_name:
            odoo_module = OdooModule.with_context(active_test=False).search([
                ('git_repository_id', '=', git_branch.repository_id.id),
                '|',
                    ('technical_name', '=', old_technical_name),
                    ('odoo_module_version_ids.old_technical_name', '=', technical_name)
                ], limit=1)
        # no existing found, create a new one
        if not odoo_module:
            # create a new module that will also create a corresponding product template with Odoo version if not exists
            # Odoo version is passed to ensure the newly created product template will have an attribute value as the same as the odoo version
            try:
                odoo_module = OdooModule.with_context(
                    odoo_version_id=odoo_version,
                    old_technical_name=old_technical_name,
                    generate_app_products=git_branch.generate_app_products
                    ).create({
                        'name': name,
                        'technical_name': technical_name,
                        'git_repository_id': git_branch.repository_id.id,
                        })
            except Exception as e:
                _logger.error(e)

        # ensure that all module have product template specified
        if not odoo_module.product_tmpl_id and git_branch.generate_app_products:
            product_tmpl_id = odoo_module._create_product_tmpl_if_not_exists()
            odoo_module.write({
                'product_tmpl_id': product_tmpl_id.id
                })
        return odoo_module

    def _create_product_if_not_exists(self):

        product_tmpl = self.module_id.product_tmpl_id
        if not product_tmpl:
            product_tmpl = self.module_id.with_context(name=self.module_id.name or self.name)._create_product_tmpl_if_not_exists()
            self.module_id.write({
                'product_tmpl_id': product_tmpl.id
                })

        product_attribute_value = self.env['product.attribute.value'].search([('odoo_version_id', '=', self.odoo_version_id.id)], limit=1)
        if not product_attribute_value:
            raise ValidationError(_("No product attribute value that matches the Odoo version %s were found!"
                                    " Please create a new product attribute value that matches this Odoo version.") % self.odoo_version_id.name)
        ProductTemplateAttributeLine = self.env['product.template.attribute.line']
        product_attribute_odoo_version_id = self.env.ref('to_product_odoo_version.product_attribute_odoo_version')

        # find the product template's attribute line that contains Odoo Version
        odoo_version_attribute_line = ProductTemplateAttributeLine.search([
            ('product_tmpl_id', '=', product_tmpl.id),
            ('attribute_id', '=', product_attribute_odoo_version_id.id)], limit=1)

        product_license_version_ids = self._context.get('product_license_version_ids', [])

        # if attribute line was found
        if odoo_version_attribute_line:
            if self.odoo_version_id not in odoo_version_attribute_line.value_ids.mapped('odoo_version_ids'):
                product_tmpl.with_context(
                    technical_name=self.technical_name,
                    product_license_version_ids=product_license_version_ids).write({
                        'attribute_line_ids':[(1, odoo_version_attribute_line.id, {
                            'value_ids':[(4, product_attribute_value.id)]
                            })]
                        })
        # not found, then create a product template attribute line for Odoo Version mapping
        else:
            product_tmpl.with_context(
                technical_name=self.technical_name,
                product_license_version_ids=product_license_version_ids).write({
                    'attribute_line_ids':[(0, 0, {
                        'attribute_id': product_attribute_odoo_version_id.id,
                        'value_ids':[(4, product_attribute_value.id)]
                        })]
                    })

        product = self.env['product.product'].with_context(active_test=False).search([
            ('product_tmpl_id', '=', product_tmpl.id),
            ('odoo_version_ids', 'in', [self.odoo_version_id.id])], limit=1)
        if not product:
            raise ValidationError(_("Could not find or create a new product for Odoo Module Version"))
        product.write({'odoo_module_version_id': self.id})
        return product

    def _prepare_module_update_data(self):
        update_data = {}
        odoo_module = self.module_id
        if odoo_module.name != self.name:
            update_data['name'] = self.name
        if odoo_module.technical_name != self.technical_name:
            update_data['technical_name'] = self.technical_name

        if not self.image_1920:
            if not odoo_module._identical_images(odoo_module.image_128, self.icon):
                update_data['image_128'] = self.icon
        else:
            if not odoo_module._identical_images(img1=odoo_module.image_1920, img2=self.image_1920):
                update_data['image_1920'] = self.image_1920

        return update_data

    def _update_module_data(self):
        """
        This method is to synchronize fields data from Module Version to Module
        """
        for r in self.filtered(lambda omv: omv.is_latest_version):
            update_data = r._prepare_module_update_data()
            if bool(update_data):
                r.module_id.write(update_data)

    def _get_vendor_price(self):
        vendor_app_comm_percent = self.get_company().vendor_app_comm_percent or 0.0
        return self.price_currency - (self.price_currency * vendor_app_comm_percent / 100.0)

    def _prepare_vendor_pricelist_data(self):
        vendor_price = self._get_vendor_price()
        return {
            'price': vendor_price,
            'currency_id': self.currency_id.id,
            'name': self.vendor_id.id,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id or self.product_id.uom_id.id,
            'min_qty': 1.0,
            'product_name': self.name,
            'product_code': self.technical_name,
            'delay': 1,
            }

    def _prepare_product_update_data(self):
        product_id = self.product_id
        update_data = {}
        if product_id.name != self.name:
            update_data['name'] = self.name
        if product_id.default_code != self.technical_name:
            update_data['default_code'] = self.technical_name
        if self.image_1920:
            if not self.module_id._identical_images(img1=product_id.image_variant_1920, img2=self.image_1920):
                update_data['image_variant_1920'] = self.image_1920
        else:
            if not self.module_id._identical_images(product_id.image_variant_128, self.icon):
                update_data['image_variant_128'] = self.icon

        if self.vendor_id:

            vendor_price = self._get_vendor_price()
            existing_vendor_pricelist = self.env['product.supplierinfo'].search([
                ('product_id', '=', product_id.id),
                ('name', '=', self.vendor_id.id),
                ('currency_id', '=', self.currency_id.id)], limit=1)
            if existing_vendor_pricelist:
                # detect if the vendor change the currency
                currency_changed = self.currency_id != existing_vendor_pricelist.currency_id

                old_price = existing_vendor_pricelist.price
                if currency_changed:
                    # compute old_price in new currency
                    old_price = existing_vendor_pricelist.currency_id._convert(old_price, self.currency_id, self.company_id, fields.Date.today())

                # check if the price has changed
                price_changed = float_compare(old_price, vendor_price, precision_rounding=self.currency_id.rounding) != 0

                if price_changed:
                    # set the existing on expired
                    update_data['seller_ids'] = [(1, existing_vendor_pricelist.id, {'date_end': fields.Date.today()})]
                    # then create a new pricelist item
                    update_data['seller_ids'] += [(0, 0, self._prepare_vendor_pricelist_data())]
            # no existing pricelist found, just create a new one
            else:
                update_data['seller_ids'] = [(0, 0, self._prepare_vendor_pricelist_data())]
        return update_data

    def _update_product_price(self):
        """
        Update module version's price to product price
        """
        ProductTemplateAttributeValue = self.env['product.template.attribute.value']
        ProductAttributeValue = self.env['product.attribute.value']
        for r in self:
            product_template_attribute_value_id = r.product_id.product_template_attribute_value_ids.filtered(lambda attr_val: attr_val.product_attribute_value_id.odoo_version_id == r.odoo_version_id)

            # not sure why r.price does not work. It returns price in the manifest's currency instead of the company's currency
            # so, we call _get_price()
            # TODO: find out why r.price does not work
            price = r._get_price()

            if product_template_attribute_value_id:
                if float_compare(product_template_attribute_value_id.price_extra, price, precision_digits=2) != 0:
                    product_template_attribute_value_id.price_extra = price
            else:
                ProductTemplateAttributeValue.create({
                    'product_attribute_value_id': ProductAttributeValue.search([('odoo_version_id', '=', r.odoo_version_id.id)], limit=1).id,
                    'product_tmpl_id': r.product_id.product_tmpl_id.id,
                    'price_extra': price,
                    })

    def _update_product_data(self):
        """
        This method is to synchronize fields data from Module Version to Product
        """
        for r in self:
            update_data = r._prepare_product_update_data()
            if bool(update_data):
                r.product_id.write(update_data)
        self._update_product_price()

    @api.model_create_multi
    def create(self, vals_list):
        ctx = self._context

        for vals in vals_list:
            OdooModule = self.env['odoo.module']

            # find odoo version
            odoo_version_id = vals.get('odoo_version_id', self._context.get('odoo_version_id', False))
            if odoo_version_id:
                if isinstance(odoo_version_id, int):
                    odoo_version_id = self.env['odoo.version'].browse(odoo_version_id)
            else:
                raise ValidationError(_("An Odoo Version is required to create a new Odoo Module Version!"))

            module_id = vals.get('module_id', self._context.get('module_id', False))
            if not module_id:
                module_id = self.with_context(
                    name=vals['name'] or vals['technical_name'],
                    technical_name=vals['technical_name'],
                    old_technical_name=vals.get('old_technical_name', ''),
                    odoo_version_id=odoo_version_id,
                    git_branch_id=vals['git_branch_id']
                    )._create_odoo_module_if_not_exists()

            elif isinstance(module_id, int):
                module_id = OdooModule.browse(module_id)

            vals['module_id'] = module_id.id

        odoo_module_versions = super(OdooModuleVersion, self).create(vals_list)
        for odoo_module_version in odoo_module_versions:
            if odoo_module_version.git_branch_id.generate_app_products:
                if not odoo_module_version.product_id:
                    product_id = odoo_module_version._create_product_if_not_exists()
                    odoo_module_version.write({
                        'product_id': product_id.id
                    })
                else:
                    odoo_module_version._update_product_data()

        # update the corresponding odoo.module record to reflect new changes from its odoo.module.version
        odoo_module_versions._update_module_data()

        # by default, generate dependencies on create
        if not ctx.get('no_generate_dependencies_on_create_write', False):
            odoo_module_versions.generate_dependencies()
        return odoo_module_versions

    def _process_update_data(self, vals):
        """
        This is mainly for potential inheritance when we need to process data in vals before update the odoo module version
        """
        self.ensure_one()
        fields_list = list(self.fields_get())
        for key in vals.keys():
            if key not in fields_list:
                vals.pop(key)
        for field in fields_list:
            if field not in vals:
                continue
            attr = getattr(self, field)
            if isinstance(attr, models.Model):
                relationship_type = self.fields_get(field, 'type')[field]['type']
                if relationship_type.lower() == 'many2one':
                    if attr.id == vals.get(field):
                        vals.pop(field)
                else:
                    # field is x2many to model, so vals[field] input prepared as [(0, 0, value)]
                    # adds a new record created from the provided dictionary values
                    for data in vals.get(field):
                        if data[0] != 0 and data[1] != 0 and not bool(data[2]):
                            vals[field].remove(data)
            elif attr == vals.get(field):
                vals.pop(field)

        if 'image_ids' not in vals:
            if self.image_ids:
                vals['image_ids'] = [(2, image.id) for image in self.image_ids]
        else:
            # check for image that already existed in db and not identical
            existing_images = {img.id: img.image for img in self.image_ids}
            result = []
            for __, __, image in vals['image_ids']:
                keep = None
                # for image in vals: set keep image to None
                # for image_id in existing_images, if image and image_id are identical: set image_id to keep, break for loop
                for image_id in existing_images.keys():
                    if self.module_id._identical_images(existing_images[image_id], image['image']):
                        keep = image_id
                        break
                # if not keep ~ image is new compare to all existing images: we create `odoo.module.version.image` image during `write()`
                # else ~ image existed: we modify existing_images to not comparing again and not removing later
                if not keep:
                    result += [(0, 0, image)]
                else:
                    existing_images.pop(keep)
            if existing_images:
                result += [(2, image_id) for image_id in existing_images.keys()]
            vals['image_ids'] = result

        return vals

    def write(self, vals):
        res = super(OdooModuleVersion, self).write(vals)
        for r in self:
            if r.product_id:
                r._update_product_data()
            else:
                # do not create product if this is a standard Odoo module
                if not r.is_standard_odoo_module and r.git_branch_id.generate_app_products:
                    product_id = r._create_product_if_not_exists()
                    r.write({
                        'product_id': product_id.id
                        })
            # only update its module data if it is the latest version
            if r.module_id.odoo_module_version_id.id == r.id:
                r._update_module_data()

        # by default, generate dependencies on write
        if 'depends' in vals and not self._context.get('no_generate_dependencies_on_create_write', False):
            self.generate_dependencies()
        return res

    def unlink(self):
        # remove the corresponding product template attribute
        product_templates = self.with_context(active_test=False).mapped('product_tmpl_id')
        product_templates.read(['attribute_line_ids', 'active'])
        product_templates.attribute_line_ids.read(['value_ids'])

        odoo_version_attribute_lines = self.env['product.template.attribute.line'].search_read([
            ('product_tmpl_id', 'in', product_templates.ids),
            ('attribute_id', '=', self.env.ref('to_product_odoo_version.product_attribute_odoo_version').id)],
            fields=['product_tmpl_id', 'id']
        )

        omvs_not_in_self = self.env['odoo.module.version'].search_read([
            ('odoo_version_id.product_attribute_value_id', 'in', self.with_context(active_test=False).mapped('odoo_version_id.product_attribute_value_id').ids),
            ('product_tmpl_id', 'in', product_templates.ids),
            ('id', 'not in', self.ids)
        ], fields=['product_tmpl_id'])

        for product_tmpl in product_templates:
            # get list of Odoo module versions to process
            to_process_odoo_module_versions = self.filtered(lambda mv: mv.product_tmpl_id == product_tmpl)
            # get list of product attribute values that are Odoo versions
            product_attribute_values = to_process_odoo_module_versions.mapped('odoo_version_id.product_attribute_value_id')

            # try to delete product variants and its template according to the Odoo version attributes
            # if the template has only one attribute line and the line has only one value, we delete the product template
            if len(product_tmpl.attribute_line_ids) == 1 and len(product_tmpl.attribute_line_ids.mapped('value_ids')) == 1:
                # trying to delete the template if it is possible

                try:
                    with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                        product_tmpl.unlink()
                # catch IntegrityError which is raised when the product is being referred by another record
                except Exception as e:
                    # set inactive
                    module_versions = to_process_odoo_module_versions.filtered(lambda mv: mv.odoo_version_id == product_attribute_values.odoo_version_id)
                    module_versions.filtered(lambda mv: mv.active).toggle_active()
                    if product_tmpl.active:
                        product_tmpl.toggle_active()
                    # could not delete product, we should keep the module also
                    self = self - to_process_odoo_module_versions

                    # log the error
                    _logger.error("Could not remove Product Template '%s' while it is being referred by another record. Details:\n%s"
                                  % (product_tmpl.name, str(e)))
            # update the attribute values to get the variants deleted automatically.
            # note that, if the variant is being referred by another record, Odoo will ignore without any error raised
            else:
                odoo_version_attribute_line = list(filter(lambda x: x['product_tmpl_id'][0] == product_tmpl.id, odoo_version_attribute_lines))
                if odoo_version_attribute_line:
                    for product_attribute_value in product_attribute_values:
                        try:
                            # Check if there are other odoo modules version link to this attribute, don't remove attribute from product template
                            if not list(filter(lambda x: x['product_tmpl_id'][0] == product_tmpl.id, omvs_not_in_self)):
                                with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                                    product_tmpl.with_context(tracking_disable=True).write({
                                        'attribute_line_ids': [(1, odoo_version_attribute_line[0]['id'], {
                                            'value_ids': [(3, product_attribute_value.id)]
                                        })]
                                    })
                        except Exception as e:
                            # set inactive
                            module_versions = to_process_odoo_module_versions.filtered(lambda mv: mv.odoo_version_id == product_attribute_value.odoo_version_id)
                            module_versions.filtered(lambda mv: mv.active).toggle_active()
                            self = self - module_versions

        # remove all images
        image_ids = self.mapped('image_ids')
        if image_ids:
            image_ids.unlink()
        modules = self.mapped('module_id')
        res = super(OdooModuleVersion, self).unlink()
        no_version_modules = modules.filtered(lambda m: m.odoo_module_versions_count == 0)
        if no_version_modules:
            no_version_modules.unlink()
        return res

    def action_view_download_stats(self):
        result = self.env['ir.actions.act_window']._for_xml_id('to_odoo_module.odoo_module_version_download_stat_action')
        result['view_mode'] = 'pivot,graph'
        res = self.env.ref('to_odoo_module.odoo_module_version_download_stat_pivot_view', False)
        result['views'] = [(res and res.id or False, 'pivot')]
        result['context'] = {'search_default_grp_module_version': True}
        result['domain'] = "[('odoo_module_version_id', 'in', %s)]" % str(self.ids)
        return result
