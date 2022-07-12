import os, glob
import ast
import logging
import base64
import lxml.html
import chardet

from pathlib import Path

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import pycompat
from odoo.tools import float_compare
from odoo.addons.to_git_odoo_version.models.git_branch import ODOO_BIN_NAMES, MANIFEST_NAMES

_logger = logging.getLogger(__name__)


def b64_image_encode(path):
    """
    @param path: the absolute path to the image file on disk

    @return: base64 encoded bytes which is ready for storing in image fields
    """
    icon_b64_encode = False
    if os.path.isfile(path):
        with open(path, 'rb') as img:
            icon_b64_encode = base64.encodebytes(img.read())
    return icon_b64_encode


def get_default_icon_b64_encode():
    current_file_path = os.path.dirname(os.path.realpath(__file__))
    this_app_dir = os.path.abspath(os.path.join(current_file_path, os.pardir))
    default_icon_path = os.path.join(this_app_dir, 'static/img/default_app_icon.png')
    return b64_image_encode(default_icon_path)


def downgrade_heading(html_doc):
    # Order is important
    heading_map = {
        'h6': 'div',
        'h5': 'h6',
        'h4': 'h5',
        'h3': 'h4',
        'h2': 'h3',
        'h1': 'h2',
        }
    for h, to_tag in heading_map.items():
        for heading in html_doc.xpath('//*[local-name() = "%s"]' % h):
            heading.tag = to_tag
    return html_doc


def parse_module_index_html(odoo_version_id, module_technical_name, index_html, downgrade_h1=True):
    """
    Read index_html file and return html string

    @return: html string or False if the index.html either does not exist or is empty
    @rtype: string
    """

    if  os.path.isfile(index_html):
        # read and parse index.html to store in the field index_html
        # this code is shamelessly copied from Odoo 11: https://github.com/odoo/odoo/blob/b277705e52232e5d28c5ec5fc381631fcb1964f8/odoo/addons/base/module/module.py#L178
        with open(index_html, 'rb') as desc_file:
            doc = desc_file.read()
            encoding = chardet.detect(doc)['encoding']
            parser = lxml.html.HTMLParser(encoding=encoding)
            html = lxml.html.document_fromstring(doc, parser=parser)
            for element, attribute, link, pos in html.iterlinks():
                if element.get('src') and not '//' in element.get('src') and not 'static/' in element.get('src'):
                    image_url = '/apps/%s/%s/static/description/%s' % (odoo_version_id.name, module_technical_name, element.get('src'))
                    element.set('src', image_url)
                    element.classes.add('img-fluid')

            # find all h1 tag
            h1 = html.xpath('//*[local-name() = "h1"]')
            # if found, downgrade all headings
            if h1:
                html = downgrade_heading(html)
            html_str = lxml.html.tostring(html, encoding='unicode')
            return tools.html_sanitize(html_str)
    return False


class GitBranch(models.Model):
    _inherit = 'git.branch'

    odoo_module_version_ids = fields.One2many('odoo.module.version', 'git_branch_id', string='Odoo Module Versions', readonly=True)
    odoo_module_versions_count = fields.Integer(string='Odoo Module Versions Count', compute='_compute_odoo_module_versions_count')
    modules_discovered_once = fields.Boolean(string='Modules Discovered', readonly=True,
                                             help="This technical field is to indicate if this branch was discovered for Odoo modules")
    last_modules_discovery = fields.Datetime(string='Last Module Discovery', readonly=True,
                                           help="This technical field is to indicate the recent date and time at which the branch was discovered"
                                           " for Odoo modules")
    auto_module_discovery = fields.Boolean(string='Auto Modules Discovery', tracking=True,
                                           help="If enabled, scanning this branch will discover Odoo modules in the branch automatically.")

    generate_app_products = fields.Boolean(string='Generate App Products', tracking=True, help="If checked, discovering Odoo modules from this"
                                           " branch will also generate app products repectively.\n"
                                           "Note: no matter this field is enabled or not, app products will NOT be generated if this branch"
                                           " contains either Odoo CE code base or Odoo Enterprise code base")

    @api.constrains('generate_app_products', 'is_odoo_enterprise_source_code', 'is_odoo_source_code')
    def _check_generate_app_products_vs_odoo_source(self):
        for r in self:
            if r.generate_app_products:
                if r.is_odoo_enterprise_source_code or r.is_odoo_source_code:
                    raise ValidationError(_("App Products should not be generated when the branch is either Odoo EE source base"
                                            " or Odoo CE source base."))

    def _update_odoo_source_code_properties(self):
        super(GitBranch, self)._update_odoo_source_code_properties()
        to_update = self.filtered(lambda b: b.generate_app_products and (b.is_odoo_enterprise_source_code or b.is_odoo_source_code))
        to_update.update({'generate_app_products': False})

    def _compute_odoo_module_versions_count(self):
        # Use sudo to allow users access the branch form view without acquiring the group Odoo Apps Management/User
        odoo_module_versions_data = self.env['odoo.module.version'].sudo().read_group([('git_branch_id', 'in', self.ids)], ['git_branch_id'], ['git_branch_id'])
        mapped_data = dict([(dict_data['git_branch_id'][0], dict_data['git_branch_id_count']) for dict_data in odoo_module_versions_data])
        for r in self:
            r.odoo_module_versions_count = mapped_data.get(r.id, 0)

    def checkout(self, _depth=0):
        # TODO(@namkazt): later we can set _depth from a config field when checkout branch
        # set _depth = 0 to fetch complete branch, _depth > 0 to fetch number of commits from HEAD
        super(GitBranch, self).checkout(_depth=_depth)

    def _parse_manifest(self, manifest_file_name, available_license_versions):
        """
        Read the manifest, parse it and prepare odoo.module.version data

        @param manifest_file_name: The full path of the manifest file (e.g. /home/git/odoo_addons/to_fleet_accounting/__manifest__.py)
        @type manifest_file_name: string

        @return: dictionary of values for creating/updating odoo module version
        @rtype: dict
        """
        self.ensure_one()

        # start preparing data
        vals = {
            'git_branch_id': self.id,
            'name': '',
            'summary': '',
            'description': '',
            'category': 'Uncategorized',
            }

        # the full path to the directory that contain the manifest file which
        module_dir = os.path.abspath(os.path.join(manifest_file_name, os.pardir))
        module_technical_name = os.path.split(module_dir)[1]
        vals['technical_name'] = module_technical_name
        odoo_module = self.env['odoo.module'].with_context(active_test=False).search([
            ('technical_name', '=', module_technical_name),
            ('git_repository_id', '=', self.repository_id.id)], limit=1)
        if odoo_module:
            vals['module_id'] = odoo_module.id

        if self.odoo_version_id:
            vals['odoo_version_id'] = self.odoo_version_id.id
        else:
            if not self._context.get('ignore_error', False):
                raise ValidationError(_("Could not find an Odoo Version that matches the git branch name '%s'."
                                        " The branch name for Odoo Apps Discovery must be in the same form as"
                                        " the one of Odoo's versions (e.g. 9.0, 10.0, 11.0, 12.0, etc)") % self.display_name)
            else:
                _logger.error(_("Could not find an Odoo Version that matches the git branch name '%s'."
                                " The branch name for Odoo Apps Discovery must be in the same form as"
                                " the one of Odoo's versions (e.g. 9.0, 10.0, 11.0, 12.0, etc)") % self.display_name)
                return {}

        # open the manifest file and eval its content and update the content into the vals
        with open(manifest_file_name, 'rb') as f:
            try:
                manifest_content = ast.literal_eval(pycompat.to_text(f.read()))
                vals.update(manifest_content)
            # ignore modules with error during literal_eval the manifest content
            # for example, the file point_of_sale/tools/posbox/overwrite_after_init/home/pi/odoo/addons/point_of_sale/__manifest__.py in Odoo 12
            # so, we catch both SyntaxError and ValueError then return {}
            # We are not sure if any other error, then we catch the general Exception also.
            except SyntaxError as e:
                _logger.error("Syntax Error during processing of the file %s. Here is the exception details: %s", manifest_file_name, e)
                # return {} to ignore the module data creation
                return {}
            except ValueError as e:
                _logger.error("ValueError during processing of the file %s. Here is the exception details: %s", manifest_file_name, e)
                # return {} to ignore the module data creation
                return {}
            except Exception as e:
                _logger.error("Exception was raised during processing of the file %s. Here is the exception details: %s", manifest_file_name, e)
                # return {} to ignore the module data creation
                return {}

        # load module's index.html
        index_html = os.path.join(module_dir, 'static/description/index.html')
        vals['index_html'] = parse_module_index_html(self.odoo_version_id, module_technical_name, index_html)

        doc_rst = os.path.join(module_dir, 'doc/index.rst')
        if  os.path.isfile(doc_rst):
            with open(doc_rst, 'r', encoding='utf-8') as f:
                vals['doc_rst'] = f.read()

        # map manifest keys with odoo.module.version fields and sanitarise the data
        if self.vendor_id:
            vals['vendor_id'] = self.vendor_id.id
        if 'author' in vals:
            vals['authors'] = vals['author']

        icon_path = os.path.join(module_dir, 'static/description/icon.png')
        icon_b64_encode = b64_image_encode(icon_path)
        default_icon_b64_encode = get_default_icon_b64_encode()
        vals['icon'] = icon_b64_encode or default_icon_b64_encode

        vals['zipped_source_code'] = self.zip_dir(module_dir)

        if 'images' in vals:
            image_ids = []
            for image in vals['images']:
                path = os.path.join(module_dir, image.strip())
                b64_image = b64_image_encode(path)
                if b64_image:
                    filename = os.path.split(path)[1]
                    # cover image
                    if filename == 'main_screenshot.png':
                        vals['image'] = b64_image
                        vals['image_1920'] = b64_image
                    # normal images
                    else:
                        image_ids.append((0, 0, {
                            'name': vals['name'],
                            'image': b64_image,
                            'filename': filename
                            }))
            if image_ids:
                vals['image_ids'] = image_ids

        # still no image, use the default one
        if 'image' not in vals:
            vals['image'] = icon_b64_encode or default_icon_b64_encode

        if 'version' not in vals:
            vals['version'] = '0.1'
        if 'depends' in vals:
            vals['depends'] = ','.join(vals['depends'])
        if not 'installable' in vals:
            vals['installable'] = True
        if not 'application' in vals:
            vals['application'] = False
        if not 'auto_install' in vals:
            vals['auto_install'] = False

        if not 'currency' in vals:
            vals['currency_id'] = self.env.company.currency_id.id
        else:
            currency_id = self.env['res.currency'].with_context(active_test=False).search([('name', '=', vals['currency'])])
            if currency_id:
                vals['currency_id'] = currency_id.id
            else:
                if self.env.company:
                    vals['currency_id'] = self.env.company.currency_id.id

        vals['price_currency'] = 0.0
        if 'price' in vals:
            # avoid nagative price which makes no sense
            if float_compare(vals['price'], 0.0, precision_digits=6) == 1:
                vals['price_currency'] = vals['price']

        if 'license' in vals:
            license_version = available_license_versions.filtered(lambda lv: lv.short_name == vals['license'])[:1]
            if not license_version:
                license_version = available_license_versions.filtered(lambda lv: lv.name == vals['license'])[:1]
            if not license_version:
                license_version = available_license_versions.filtered(lambda lv: lv.name.lower() == vals['license'].lower())[:1]
            if not license_version:
                license_version = available_license_versions.filtered(lambda lv: lv.name.lower() in vals['license'].lower())[:1]
            if license_version:
                vals['license_version_id'] = license_version.id
            else:
                vals['license_version_id'] = self.env.ref('to_product_license.license_version_lgpl_v3').id
        else:
            branch_licence_version = self.get_license_version()
            vals['license_version_id'] = branch_licence_version.id or self.env.ref('to_product_license.license_version_opl_v1').id

        if 'category' in vals:
            category_id = self.env['ir.module.category'].sudo().guess_category_from_string(vals['category'])
            if category_id:
                vals['ir_module_category_id'] = category_id.id

        return vals

    def _prepare_odoo_module_data(self, manifest_file_name, available_license_versions):
        """
        remove unsupported keys which cannot be mapped with the fields of the odoo.module.version
        """
        vals = self._parse_manifest(manifest_file_name, available_license_versions=available_license_versions)

        # remove unsupported keys which cannot be mapped with the fields of the odoo.module.version
        fields_list = list(self.env['odoo.module.version'].fields_get())
        keys = list(vals)
        for k in keys:
            if k not in fields_list:
                vals.pop(k, None)
            else:
                if k in self.env['odoo.module.version']._get_manifest_description_keys():
                    vals[k] = vals[k].strip()
        return vals

    def _verify_module_manifest_location(self, manifest_file):
        """
        This method helps us to verify if the module directory of the given manifest_file is in either
        of the following directories
            1. /path/to/odoo/addons (Odoo source code branch)
            2. /path/to/odoo/odoo/addons (Odoo source code branch for Odoo 10 or later)
            3. /path/to/odoo/openerp/addons (Odoo source code branch for Odoo 9 or earlier)
            4. /path/to/standalone/addons

        :param: manifest_file: full path to the <MANIFEST_NAMES> file in string
        :type manifest_file: string

        :return: True if the module directory of the given manifest_file is in either
            of the above mentioned directories
        """
        self.ensure_one()

        # convert to pathlib.Path
        manifest_file = Path(manifest_file)
        # return false if the given manifest_file is not a file or does not exist or not a valid manifest name
        if not manifest_file.exists() or manifest_file.name not in MANIFEST_NAMES:
            return False

        # if the manifest file is located under 2-level down of the working tree,
        # it's surely a valid Odoo module
        if not self.is_odoo_source_code and manifest_file.parent.parent == Path(self.working_tree):
            return True

        # if inside Odoo source code
        if any(
            # /path/to/odoo
            manifest_file.parent.parent.parent.joinpath(odoo_bin_name).exists() \
            or manifest_file.parent.parent.parent.parent.joinpath(odoo_bin_name).exists() \
            for odoo_bin_name in ODOO_BIN_NAMES
            ):
            return True

        return False

    def _discover_odoo_modules(self):
        # always use English to ensure to not override translations
        # And, for performance, generate dependencies will not be done upon create/write
        # we will do it later when all module versions have been discovered
        self = self.with_context(
            lang='en_US',
            no_generate_dependencies_on_create_write=True,
        )

        odoo_module_versions = self.env['odoo.module.version']
        available_license_versions = self.env['product.license.version'].search([])

        # sort branches in self by Odoo version ascending
        self = self.sorted_by_odoo_version()

        for r in self:
            existing_module_versions = self.env['odoo.module.version'].with_context(active_test=False).search([
                ('odoo_version_id', '=', r.odoo_version_id.id),
                ('git_branch_id', '=', r.id),
                ])
            for manifest_name in MANIFEST_NAMES:
                # recursively search for manifest files in the branch's working_tree
                for manifest_file_name in glob.iglob(r.working_tree + '/**/' + manifest_name, recursive=True):
                    if not r._verify_module_manifest_location(manifest_file_name):
                        continue
                    # prepare module data
                    odoo_module_data = r._prepare_odoo_module_data(manifest_file_name, available_license_versions)
                    if bool(odoo_module_data):
                        try:
                            with r.env.cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                                odoo_module_version = existing_module_versions.filtered(lambda v: v.technical_name == odoo_module_data.get('technical_name'))
                                if odoo_module_version:
                                    for v in odoo_module_version:
                                        vals = odoo_module_data.copy()
                                        vals = v._process_update_data(vals)
                                        v.with_context(update_when_discover=True).write(vals)
                                        _logger.debug(
                                            "Updated the module '%s [%s]' from the branch '%s'.",
                                            v.name,
                                            v.technical_name,
                                            r.display_name
                                            )
                                else:
                                    odoo_module_version = self.env['odoo.module.version'].with_context(
                                        odoo_version_id=r.odoo_version_id
                                        ).create(odoo_module_data)
                                    existing_module_versions |= odoo_module_version
                                    _logger.debug(
                                        "Generated the module '%s [%s]' from the branch '%s'.",
                                        odoo_module_version.name,
                                        odoo_module_version.technical_name,
                                        r.display_name
                                        )
                                odoo_module_versions |= odoo_module_version

                        except Exception as e:
                            _logger.error(
                                "There was an error discovering Odoo module '%s' (%s) in the branch %s of the repository %s. Here is detail error message: %s",
                                odoo_module_data.get('name', 'unknown'),
                                manifest_file_name,
                                r.name,
                                r.repository_id.name,
                                e
                                )
            update_vals = {
                'last_modules_discovery': fields.Datetime.now()
                }
            # mark as discovered once
            if not r.modules_discovered_once:
                update_vals['modules_discovered_once'] = True
            r.write(update_vals)

        # remove the modules that no longer exist in their corresponding branches
        branches = odoo_module_versions.mapped('git_branch_id')
        current_module_versions = self.env['odoo.module.version'].with_context(active_test=False).search([('git_branch_id', 'in', branches.ids)])
        to_remove = current_module_versions - odoo_module_versions
        to_remove.unlink()
        odoo_module_versions = odoo_module_versions.exists()

        # synch licenses from module versions to products
        product_ids = odoo_module_versions.mapped('product_id')
        product_ids.synch_licenses_from_odoo_module_versions()

        # all module versions have been discovered, generate dependencies now
        odoo_module_versions.generate_dependencies()
        odoo_module_versions.generate_authors()
        return odoo_module_versions

    def action_discover_odoo_modules(self):
        for r in self:
            if not r.checked_out:
                raise ValidationError(_("The branch '%s' of the repository '%s' is not checked out. Please do checkout first!")
                                      % (r.name, r.repository_id.name))
        if not self.env.su:
            if not self.env.user.has_group('to_odoo_module.odoo_module_user'):
                raise UserError(_("Sorry, you don't have the permission for this operation. This operation is allowed for the group: \n\t - Odoo Apps/User"))
            else:
                return self.sudo()._discover_odoo_modules()
        return self._discover_odoo_modules()

    def action_view_odoo_module_versions(self):
        odoo_module_versions = self.mapped('odoo_module_version_ids')
        result = self.env['ir.actions.act_window']._for_xml_id('to_odoo_module.odoo_module_version_action')

        # get rid off the default context
        result['context'] = {}

        # choose the view_mode accordingly
        modules_count = len(odoo_module_versions)
        if modules_count != 1:
            result['domain'] = "[('git_branch_id', 'in', " + str(self.ids) + ")]"
        elif modules_count == 1:
            res = self.env.ref('to_odoo_module.odoo_module_version_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = odoo_module_versions.id
        return result

    def action_pull(self):
        """
        This may be called by cron
        """
        res = super(GitBranch, self).action_pull()
        ignore_error = self._context.get('ignore_error', False)
        # auto discover Odoo modules on branches that are set with Auto Modules Discovery
        if ignore_error:
            branch_ids = self.filtered(lambda b: b.auto_module_discovery and b.checked_out)
        else:
            branch_ids = self.filtered(lambda b: b.auto_module_discovery)
        if branch_ids:
            branch_ids.action_discover_odoo_modules()
        return res

    def _get_auto_scan_branches(self):
        branches = super(GitBranch, self)._get_auto_scan_branches()
        # sort branches by Odoo version ascending
        branches = branches.sorted_by_odoo_version()
        return branches

    def unlink(self):
        odoo_module_versions = self.mapped('odoo_module_version_ids')
        if odoo_module_versions:
            odoo_module_versions.unlink()
        return super(GitBranch, self).unlink()

