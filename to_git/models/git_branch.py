import logging
import os
import shutil
import multiprocessing
import urllib.parse

from docutils.core import publish_string

_logger = logging.getLogger(__name__)

try:
    from git import Git, GitCommandError
except ImportError:
    _logger.error("GitPython is not installed. Please fire the command pip install GitPython to install it")

from odoo import models, fields, api, tools, registry, _
from odoo.exceptions import UserError
from odoo.addons.base.models.ir_module import MyWriter

from .. import helper


class GitBranch(models.Model):
    _name = 'git.branch'
    _order = 'sequence ASC, repository_id ASC, name ASC, id'
    _description = 'Git Branch'
    _inherit = 'mail.thread'

    name = fields.Char(required=True, help="Name of the git branch")
    sequence = fields.Integer(related='repository_id.sequence', store=True, index=True)
    repository_id = fields.Many2one('git.repository', required=True,
                                    ondelete='cascade')
    is_default = fields.Boolean(
        string='Default', tracking=True,
        help='This is to indicate that the branch is the default in the repository')
    checked_out = fields.Boolean(compute='_compute_checked_out', search='_search_checkout')
    working_tree = fields.Char(compute='_get_working_tree',
        help='Path to the working tree of the branch.')
    recent_pull_time = fields.Datetime()
    head_commit = fields.Char(compute='_compute_head_commit')
    detached_head = fields.Boolean(compute='_compute_detached_head')
    auto_scan = fields.Boolean(string='Auto Scan', tracking=True,
                               help="If checked, this branch will be regularly scanned for updates")
    vendor_id = fields.Many2one(related='repository_id.vendor_id', store=True, readonly=True, index=True,
                                help="The partner who holds the copyright of this branch's repository")
    company_id = fields.Many2one(related='repository_id.company_id', store=True, index=True, readonly=True, help="The company to which the"
                                " branch belong.")

    _sql_constraints = [
        ('name_repository_id_unique',
         'UNIQUE(name, repository_id)',
         "Branch name must be unique per repository!"),
    ]

    @api.constrains('name', 'repository_id')
    def _check_name_vs_repository(self):
        # avoid unnecessary checking if branch created by scanning
        if self.env.context.get('skip_check_branch_name'):
            return

        for r in self:
            if r.name and r.repository_id:
                remote_branch_names, remote_default_branch = r.repository_id._ls_remote()
                if r.name not in remote_branch_names:
                    raise UserError(_("The branch name %s you've entered is not available in the remote repository %s.")
                                    % (r.name, r.repository_id.name))

    @api.constrains('auto_scan', 'repository_id')
    def _check_with_credential_auto_scan(self):
        for r in self:
            if r.auto_scan:
                if r.repository_id.with_credential:
                    raise UserError(_("You can not mark Auto Scan for the branch %s of the repository %s while the repository may require credential."
                                      " Please consider to use SSH protocol with SSH Key for the repositories that you want to get auto scanned.\n"
                                      "If you are sure that there is no credential to be required, please:\n"
                                      "1. Refesh your browser (press Command + R if you are on Mac, or F5 if you are on Windows/Linux),\n"
                                      "2. Checkout or pull the branch,\n"
                                      "3. Set Auto Scan again.")
                                      % (r.name, r.repository_id.name))
                if not r.checked_out:
                    raise UserError(_("You must check out the branch before you can set auto scan"))

    @api.depends('working_tree')
    def _compute_checked_out(self):
        for r in self:
            r.checked_out = os.path.isdir(r.working_tree)

    @api.model
    def _search_checkout(self, operator, operand):
        all_branches = self.search([])
        if operator == '=':
            return [('id', 'in', all_branches.filtered(lambda b: b.checked_out == operand).ids)]
        else:
            return [('id', 'not in', all_branches.filtered(lambda b: b.checked_out == operand).ids)]

    def _compute_head_commit(self):
        for r in self:
            if not r.checked_out:
                r.head_commit = None
                continue
            try:
                git = Git(r.working_tree)
                head_commit = git.log('--oneline', '--no-decorate', '-1')
                r.head_commit = head_commit
            except:
                r.head_commit = False

    def _compute_detached_head(self):
        for r in self:
            if not r.checked_out:
                r.detached_head = None
                continue
            try:
                git = Git(r.working_tree)
                status = git.status()
                r.detached_head = status.startswith('HEAD detached')
            except:
                r.detached_head = False

    def _get_working_tree(self):
        git_data_path = helper.git_data_path()
        for r in self:
            r.working_tree = os.path.join(git_data_path, str(r.repository_id.id), 'working_trees', r.name)

    @helper.rerun_with_credentials
    def checkout(self, _depth=0):
        """
        Fetch and checkout a branch to a new working tree.
        """
        for r in self:
            if r.checked_out:
                continue
            with_credential = r._context.get('with_credential', False)
            # mark the repository that the credential is required
            if with_credential and not r.repository_id.with_credential:
                r.repository_id.write({'with_credential': True})

            git = Git(r.repository_id.path)
            url = r.repository_id.remote_url_with_credentials()
            refspec = '{0}:{0}'.format(r.name)
            # get optimize job amount
            jobs_count = multiprocessing.cpu_count() or 1
            try:
                if _depth:
                    git.fetch(url, refspec, depth=_depth, jobs=jobs_count, env=r.repository_id._get_git_env())
                else:
                    git.fetch(url, refspec, jobs=jobs_count, env=r.repository_id._get_git_env())
            except GitCommandError as e:
                r.repository_id.check_credentials()
                message = _('Failed to fetch data from the remote!\n'
                            'Please make sure that you have a working network connection, '
                            'the repository exists and you have the correct access rights.')
                if e.stderr:
                    message += '\n' + e.stderr
                raise UserError(message)
            try:
                git.worktree('add', r.working_tree, r.name)
            except GitCommandError as e:
                message = _("Failed to checkout the branch '%s'!") % r.display_name
                if e.stderr:
                    message += '\n' + e.stderr
                raise UserError(message)
            r.recent_pull_time = fields.Datetime.now()

            # if we can come here and not with_credential, it means that the repo does not require credential
            if not with_credential and r.repository_id.with_credential:
                r.repository_id.write({'with_credential': False})
        self._compute_checked_out()
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def un_checkout(self):
        """
        Undo checkout the branch from the repository. For cache purpose,
        only the working tree of the branch is removed, the branch
        itself still exists in the repository.
        """
        for r in self:
            if not r.checked_out:
                continue
            git = Git(r.repository_id.path)
            try:
                git.worktree('remove', '--force', r.working_tree)
            except GitCommandError as e:
                message = _('Failed to remove the working tree of the branch!')
                if e.stderr:
                    message += '\n' + e.stderr
                raise UserError(message)
            r.recent_pull_time = None
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @helper.rerun_with_credentials
    def action_checkout(self):
        self.filtered(lambda b: not b.checked_out).checkout()

    @helper.rerun_with_credentials
    def pull(self):
        """
        Update the branch for latest changes from the remote repository.

        If the working tree is currently in detached HEAD state,
        we do git fetch instead of git pull to avoid unwanted merging.
        """
        for r in self:
            ignore_error = r._context.get('ignore_error', False)
            if not r.checked_out:
                r.checkout()
                continue
            with_credential = r._context.get('with_credential', False)
            # mark the repository that the credential is required
            if with_credential and not r.repository_id.with_credential:
                r.repository_id.write({'with_credential': True})
            git = Git(r.working_tree)
            url = r.repository_id.remote_url_with_credentials()
            try:
                git.fetch(url, r.name, env=r.repository_id._get_git_env())
            except GitCommandError as e:
                if ignore_error:
                    continue
                r.repository_id.check_credentials()
                message = _('Failed to fetch data from the remote!\n'
                            'Please make sure that you have a working network connection, '
                            'the repository exists and you have the correct access rights.')
                if e.stderr:
                    message += '\n' + e.stderr
                raise UserError(message)
            r.recent_pull_time = fields.Datetime.now()
            if r.detached_head:
                continue
            try:
                git.reset('--hard', 'FETCH_HEAD')
            except GitCommandError as e:
                if ignore_error:
                    continue
                message = _('Failed to update the working tree!')
                if e.stderr:
                    message += '\n' + e.stderr
                raise UserError(message)
            # if we can come here and not with_credential, it means that the repo does not require credential
            if not with_credential and r.repository_id.with_credential:
                r.repository_id.write({'with_credential': False})
        return

    def _update_gitdir(self):
        """
        When we move the Odoo instance to another server, git data dir would probably change accordingly
        while its gitdir still refers to old ones. I.e.
            Old Paths:
                /old_path/to/filestore/db_name/git/{repo_id}/working_trees/{branch_name}/.git
                /old_path/to/filestore/db_name/git/{repo_id}/repo/worktrees/{branch_name}/gitdir
            New Paths:
                /new_path/to/filestore/db_name/git/{repo_id}/working_trees/{branch_name}/.git
                /new_path/to/filestore/db_name/git/{repo_id}/repo/worktrees/{branch_name}/gitdir

        This method fixed these gitdir information
        """

        def get_git_data_path(path, repo_id_str):
            """
            Extract from path for the git data path. I.e.
            '/any/thing/here/{repo_id}/any/thing/else/here' will return '/any/thing/here'
            """
            head, tail = os.path.split(path)
            while tail != repo_id_str and tail != '':
                head, tail = os.path.split(head)
            return head

        git_data_path = helper.git_data_path()
        for r in self:
            files = [
                # /path/to/filestore/db_name/git/{repo_id}/working_trees/{branch_name}/.git
                os.path.join(r.working_tree, '.git'),
                # /path/to/filestore/db_name/git/{repo_id}/repo/worktrees/{branch_name}/gitdir
                os.path.join(git_data_path, str(r.repository_id.id), 'repo', 'worktrees', r.name, 'gitdir')
                ]
            for file in files:
                new_content = False
                try:
                    with open(file, 'r') as f:
                        content = f.read()
                        gitdir = content.split(' ')[-1]
                        old_git_data_path = get_git_data_path(gitdir, str(r.repository_id.id))
                        if old_git_data_path != git_data_path:
                            new_content = content.replace(old_git_data_path, git_data_path)
                except FileNotFoundError as e:
                    continue
                if new_content:
                    with open(file, 'w') as f:
                        f.write(new_content)

    @helper.rerun_with_credentials
    def action_pull(self):
        """
        wrapper for pull.
        This may help avoid helper decorators in future inheritance
        """
        branches = self.filtered(lambda b: b.checked_out)
        branches._update_gitdir()
        return branches.pull()
    
    def _get_auto_scan_branches_domain(self):
        return [('auto_scan', '=', True)]
    
    def _get_auto_scan_branches(self):
        return self.search(self._get_auto_scan_branches_domain())

    def cron_scan(self):
        branches = self._get_auto_scan_branches()
        org_cr = branches._cr
        returned_branches = self.env['git.branch']
        for branch in branches.filtered(lambda b: b.checked_out):
            _logger.debug("Started to scan the git branch %s", branch.display_name)
            cr = registry(org_cr.dbname).cursor()
            branch = branch.with_env(branch.env(cr=cr)).with_context(ignore_error=True)
            try:
                branch.action_pull()
                cr.commit()
                _logger.debug("Successfully scanned the git branch %s", branch.display_name)
                branch.clear_caches()
                branch = branch.with_env(branch.env(cr=org_cr))
                returned_branches |= branch
            except Exception as e:
                cr.rollback()
                _logger.error("Error occurred during scanning the git branch %s. Here is details: %s", branch.display_name, str(e))
                branch = branch.with_env(branch.env(cr=org_cr))
            finally:
                cr.close()

        if returned_branches:
            _logger.debug("Successfully scanned %s branches: %s", len(returned_branches), ', '.join(returned_branches.mapped('display_name')))
        failed_branches = branches - returned_branches
        if failed_branches:
            _logger.debug("Failed to scan %s branches: %s", len(failed_branches), ', '.join(failed_branches.mapped('display_name')))
        return returned_branches

    def recent_commits(self, limit=10):
        """
        Get recent commits in the branch.
        """
        self.ensure_one()
        git = Git(self.working_tree)
        try:
            log = git.log('--oneline', '--no-decorate', '-{}'.format(limit),
                          self.name)
        except GitCommandError as e:
            message = _('Failed to get recent commits!')
            if e.stderr:
                message += '\n' + e.stderr
            raise UserError(message)
        vals_list = []
        for line in log.splitlines():
            cols = line.split(' ', 1)
            commit_value = {'hash': cols[0], 'message': cols[1]}
            vals_list.append(commit_value)
        return self.env['git.commit'].create(vals_list)

    def checkout_commit(self, commit_hash):
        """
        Checkout a specific commit in the branch to the working tree.
        """
        self.ensure_one()
        git = Git(self.working_tree)
        try:
            out = git.branch('--contains', commit_hash, '--points-at=' + self.name)
        except GitCommandError as e:
            message = _('The commit does not exist!')
            if e.stderr:
                message += '\n' + e.stderr
            raise UserError(message)
        if not out:
            message = _('The commit is not in this branch!')
            raise UserError(message)
        try:
            git.checkout(commit_hash)
        except GitCommandError as e:
            message = _('Failed to checkout the commit!')
            if e.stderr:
                message += '\n' + e.stderr
            raise UserError(message)

    def reset_head(self):
        """
        Reset the working tree to latest commit in the branch.
        """
        failed_branches = []
        for r in self:
            if not r.checked_out:
                continue
            git = Git(r.working_tree)
            try:
                git.checkout(r.name)
            except GitCommandError:
                failed_branches.append(r.name)
        if failed_branches:
            message = _('Failed to reset the branches: ')
            message += ', '.join(failed_branches)
            raise UserError(message)

    def reset_to_head(self):
        """
        Reset the working tree to it's HEAD.
        """
        failed_branches = []
        for r in self:
            if not r.checked_out:
                continue
            git = Git(r.working_tree)
            try:
                git.reset('--hard', 'HEAD')
            except GitCommandError:
                failed_branches.append(r.name)
        if failed_branches:
            message = _('Failed to reset to HEAD for the branches: ')
            message += ', '.format(failed_branches)
            raise UserError(message)

    def action_reset_to_head(self):
        self.reset_to_head()

    def action_update_gitdir(self):
        self._update_gitdir()

    def disable_auto_scan(self):
        """
        This will disable auto scan for all the branches in self
        """
        branch_ids = self.filtered(lambda b: b.auto_scan)
        if branch_ids:
            branch_ids.write({'auto_scan': False})

    def unlink(self):
        paths = self.mapped('working_tree')
        for r in self:
            if r.checked_out:
                r.un_checkout()
        res = super(GitBranch, self).unlink()
        for path in paths:
            try:
                shutil.rmtree(path)
            # if the branch is not checked_out, FileNotFoundError will be raised
            except FileNotFoundError:
                pass
        return res

    def zip_dir(self, path):
        """
        zip a directory tree into a bytes object which is ready for storing in Binary field.
        This is a wrapper for to.base's zip_dir

        @param path: the path to the directory to zip
        @type path: string
        
        @return: return bytes object containing data for storing in Binary fields
        @rtype: bytes
        """
        return self.env['to.base'].zip_dir(path, incl_dir=True)

    def zip_dirs(self, paths):
        """
        zip a tree of directories (defined by paths) into a bytes object which is ready for storing in Binary field

        @param paths: list of absolute paths (string) to the directories to zip
        @type paths: list
        
        @return: return bytes object containing data for storing in Binary fields
        @rtype: bytes
        """
        return self.env['to.base'].zip_dirs(paths)

    def rst2html(self, rst):
        overrides = {
            'embed_stylesheet': False,
            'doctitle_xform': False,
            'output_encoding': 'unicode',
            'xml_declaration': False,
            'file_insertion_enabled': False,
            }
        output = publish_string(source=rst or '', settings_overrides=overrides, writer=MyWriter())
        return tools.html_sanitize(output)

    def name_get(self):
        # prefetching
        self.read(['repository_id', 'name'])
        result = []
        for r in self:
            result.append((r.id, '%s#%s' % (r.repository_id.remote_url, r.name)))
        return result

    def parse_git_url(self, git_url):
        """
        :param git_url: the git URL that should follow a standardized format: ssh://git@github.com/odoo/odoo.git#git_branch_name
        :return: ParseResult object containing scheme, netloc, path, params, query, fragment. E.g.
            ParseResult(scheme='ssh', netloc='git@git.tvtmgroup.com:3300', path='/customer/american-learning-lab/customs.git', params='', query='', fragment='')
        :rtype: ParseResult
        """
        
        contain_protocol = git_url.find('://') >= 0
        # since GitHub URL may contain ':' which is not a port for SSH, we should replace it with '/'
        if not contain_protocol and git_url.find('github.com') > 0:
            git_url = git_url.replace(':', '/')

        # assume ssh if no protocol found
        if not contain_protocol:
            git_url = 'ssh://' + git_url

        return urllib.parse.urlparse(git_url)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('repository_id.netloc', '=ilike', '%' + name + '%'), ('repository_id.netpath', '=ilike', '%' + name + '%'), ('name', operator, name)]
        branches = self.search(domain + args, limit=limit)
        return branches.name_get()
