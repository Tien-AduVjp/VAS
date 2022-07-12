import os
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.to_git import helper

_logger = logging.getLogger(__name__)

ODOO_BIN_NAMES = ('openerp-server', 'odoo.py', 'odoo-bin')
MANIFEST_NAMES = ('__manifest__.py', '__openerp__.py')


class GitBranch(models.Model):
    _inherit = 'git.branch'

    odoo_version_id = fields.Many2one('odoo.version', string='Odoo Version', readonly=True, auto_join=True)
    contain_odoo_module = fields.Boolean(string='Odoo Addons Inside', readonly=True)
    is_odoo_source_code = fields.Boolean(string='Is Odoo Source Code', readonly=True,
                                           help="This field indicates if the branch stores Odoo's source code base, which is also known as Odoo CE.\n"
                                           "Note: The value of this field will be updated automatically when the branch will be updated from remote git.")
    is_odoo_enterprise_source_code = fields.Boolean(related='repository_id.is_odoo_enterprise_source_code', string='Is Odoo Enterprise',
                                                    store=True, readonly=True,
                                                    help="This field indicates if this branch is Odoo Enterprise source base that contains Odoo Enterprise"
                                                    " modules built on top of Odoo CE")
    default_license_version_id = fields.Many2one('product.license.version', string='Default License Version', help="Unless otherwise specified"
                                                 " (e.g. in the module's manifest), all the source code of this branch will be considered as"
                                                 " being released under this license.")
    depending_git_branch_ids = fields.Many2many('git.branch', 'depending_git_branch_rel', 'depended_branch_id', 'depending_branch_id', string='Depending Branches',
                                                help="The external git branches on which this branch depends.")
    depended_git_branch_ids = fields.Many2many('git.branch', 'depending_git_branch_rel', 'depending_branch_id', 'depended_branch_id', string='Depended Branches',
                                                help="The external git branches that depend on this branch.")

    @api.constrains('depending_git_branch_ids', 'odoo_version_id')
    def _check_depending_git_branches(self):
        for r in self:
            if r.odoo_version_id:
                for b in r.depending_git_branch_ids.filtered(lambda b: b.odoo_version_id and b.odoo_version_id != r.odoo_version_id):
                    raise ValidationError(_("Odoo Version Discrepancy between the branch %s and the depending branch %s")
                                          % (r.display_name, b.display_name))

    @api.constrains('depended_git_branch_ids', 'odoo_version_id')
    def _check_depended_git_branches(self):
        for r in self:
            if r.odoo_version_id:
                for b in r.depended_git_branch_ids.filtered(lambda b: b.odoo_version_id and b.odoo_version_id != r.odoo_version_id):
                    raise ValidationError(_("Odoo Version Discrepancy between the branch %s and the depended branch %s")
                                          % (r.display_name, b.display_name))

    def _get_recursive_depending_branches(self, incl_the_current=False):
        """
        Do not call this from external. This is a private method.
        """
        branch_ids = self.mapped('depending_git_branch_ids')

        if incl_the_current:
            branch_ids |= self

        for branch_id in branch_ids:
            branch_ids |= branch_id.get_recursive_depending_branches(incl_the_current=False)

        return branch_ids

    def get_recursive_depending_branches(self, incl_the_current=False, reverse=False):
        """
        Wrapper for the _get_recursive_depending_branches()
        In this method, we may improve more. For example, add sorting function.
        """
        return self._get_recursive_depending_branches(incl_the_current=incl_the_current).sorted(key=None, reverse=True)

    def get_license_version(self):
        return self.default_license_version_id or self.repository_id.default_license_version_id

    @api.constrains('is_odoo_source_code', 'is_odoo_enterprise_source_code')
    def _check_is_odoo_source_code_vs_is_odoo_enterprise_source_code(self):
        for r in self:
            if r.is_odoo_source_code and r.is_odoo_enterprise_source_code:
                raise ValidationError(_("The branch %s cannot be both Odoo Source Code and Odoo Enterprise Source Code.") % r.display_name)

    def _update_odoo_version(self, vals):
        if 'name' in vals:
            odoo_version_id = self.env['odoo.version'].search([('name', '=', vals['name'])], limit=1)
            if odoo_version_id:
                vals['odoo_version_id'] = odoo_version_id.id
        return vals

    def _assign_odoo_version(self):
        for r in self:
            odoo_version_id = self.env['odoo.version'].search([('name', '=', r.name)], limit=1)
            if not odoo_version_id:
                continue
            if not r.odoo_version_id or r.name != odoo_version_id.name:
                r.write({
                    'odoo_version_id': odoo_version_id.id
                    })

    def action_assign_odoo_version(self):
        self._assign_odoo_version()

    def _get_auto_scan_branches(self):
        """
        Override to ensure branches are sorted by their Odoo versions ascendingly
        """
        branches = super(GitBranch, self)._get_auto_scan_branches()
        return branches.sorted_by_odoo_version()

    def sorted_by_odoo_version(self):
        """
        sort the branches in self by their Odoo versions ascendingly
        
        :return: recordset of sorted branches
        """
        try:
            # sort the branches in self by their Odoo version's full_version_str
            # Hint: list(map(int, [x if x.isdigit() else '0' for x in v.odoo_version_id.name.split('.')])) will
            # return a list like [12, 0, 6, 2, 1] presenting '12.0.6.2.1'. Any non-digit will be converted to 0.
            # For example, '12.0.6.2.beta' will become '12.0.6.2.0'
            return self.sorted(key=lambda v: list(map(int, [x if x.isdigit() else '9' for x in (v.odoo_version_id.name.split('.') if v.odoo_version_id else v.name.split('.'))])), reverse=False)
        except Exception as e:
            _logger.error("There is an error during sorting branches by Odoo versions. Here is the details:\n%s", e)
            return self

    def _is_odoo_source_code(self):
        is_odoo_source_code = False
        for file_name in ODOO_BIN_NAMES:
            full_path = self.working_tree + '/' + file_name
            if os.path.isfile(full_path):
                is_odoo_source_code = True
                break
        return is_odoo_source_code

    def _contain_odoo_module(self):
        """
        Test if the working tree contain at least one valid odoo module,
        which has one of the manifest files (__openerp__.py, __manifest__.py) inside

        @rtype: bool
        """
        self.ensure_one()
        for f in os.listdir(self.working_tree):
            modpath = os.path.join(self.working_tree, f)
            if os.path.isdir(modpath):
                if any(os.path.isfile(os.path.join(modpath, mname)) for mname in MANIFEST_NAMES):
                    return True
        return False

    def _update_odoo_source_code_properties(self):
        for r in self:
            data = {
                'is_odoo_source_code': r._is_odoo_source_code(),
                'contain_odoo_module': r._contain_odoo_module()
                }
            r.update(data)

    @helper.rerun_with_credentials
    def action_checkout(self):
        super(GitBranch, self).action_checkout()
        self._update_odoo_source_code_properties()

    @helper.rerun_with_credentials
    def action_pull(self):
        res = super(GitBranch, self).action_pull()
        self._update_odoo_source_code_properties()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update(self._update_odoo_version(vals))
        return super(GitBranch, self).create(vals_list)

    def write(self, vals):
        vals = self._update_odoo_version(vals)
        return super(GitBranch, self).write(vals)
