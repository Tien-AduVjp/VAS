import logging
import os
import shutil
import stat
import urllib.parse

_logger = logging.getLogger(__name__)

try:
    from git import Git, Repo, GitCommandError
except ImportError:
    _logger.error("GitPython is not installed. Please fire the command pip install GitPython to install it")

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from .. import helper


class GitRepository(models.Model):
    """
    Represent for a bare git repository.
    """
    _name = 'git.repository'
    _inherit = 'mail.thread'
    _order = 'sequence ASC, id'
    _description = 'Git Repository'

    name = fields.Char(required=True, compute='_compute_name', store=True, readonly=False,
                       help="Name of the repository",
                       tracking=True)
    sequence = fields.Integer(string='Sequence', default=99999, help="This help prior the auto scanning.")

    # Git URL format ref: https://git-scm.com/docs/git-clone#_git_urls_a_id_urls_a
    remote_url = fields.Char(
        required=True,
        help="Remote URL of the repository. For examples:\n"
             "ssh://[user@]host.xz[:port]/path/to/repo.git/\n"
             "http[s]://[user:password@]host.xz[:port]/path/to/repo.git/\n"
             "[user@]host.xz:path/to/repo.git/",
        tracking=True)
    netloc = fields.Char(string='Net Location', compute='_compute_net_resources', store=True, help="The location of the resource. For example, 'github.com'.")
    domain_name = fields.Char(string='Remote Domain Name', compute='compute_domain_name', store=True)
    netpath = fields.Char(string='Net Path', compute='_compute_net_resources', store=True, help="The path of the resource. For example, '/odoo/odoo'.")
    scheme = fields.Selection([('ssh', 'SSH'), ('http', 'HTTP'), ('https', 'HTTPS')], string='Scheme', compute='_compute_net_resources', store=True)
    path = fields.Char(compute='_get_repo_path', help='Path to the repository')
    branch_ids = fields.One2many('git.branch', 'repository_id', string='Branches')
    branches_count = fields.Integer(string='Branches Count', compute='_compute_branches_count')
    vendor_id = fields.Many2one('res.partner', string='Vendor', tracking=True, help="The partner who holds the copyright of this repository."
                                " Leave it empty if this is a repository of your company's.")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True,
                                 help="The company to which the repository belong. Leave this field empty to make this available to all"
                                 " the companies in the system.")
    with_credential = fields.Boolean(string='With Credential', default=True, readonly=True,
                                     help="Technical field to indicate if the repository requires credential."
                                     " We assume all new repositories require credential")
    parent_id = fields.Many2one('git.repository', string='Forked From', help="This field is to indicate the parent repository from which this repository was forked.")
    child_ids = fields.One2many('git.repository', 'parent_id', string='Forks')
    forks_count = fields.Integer(string='Forks Count', compute='_compute_forks_count')
    ssh_key_id = fields.Many2one('sshkey.pair', string='SSH Key', groups='to_sshkey.group_sshkey_manager')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The git repository name must be unique!"),

        ('remote_url_unique',
         'UNIQUE(remote_url)',
         "The git repository url must be unique!"),
    ]

    @api.constrains('parent_id')
    def _check_parent_id(self):
        for r in self:
            if r.parent_id and r.parent_id.id == r.id:
                raise UserError(_("The repository %s cannot be a fork of itselves.") % r.display_name)

    @api.depends('parent_id')
    def _compute_forks_count(self):
        forks_data = self.read_group([('parent_id', 'in', self.ids)], ['parent_id'], ['parent_id'])
        mapped_data = dict([(dict_data['parent_id'][0], dict_data['parent_id_count']) for dict_data in forks_data])
        for r in self:
            r.forks_count = mapped_data.get(r.id, 0)

    @api.constrains('domain_name', 'netpath')
    def _check_unique_repo(self):
        for r in self:
            existing = self.search([('id', '!=', r.id), ('domain_name', '=', r.domain_name), ('netpath', '=', r.netpath)], limit=1)
            if existing:
                raise ValidationError(_("The repository %s%s already exsits") % (r.netloc, r.netpath))

    def _parse_url(self):
        return self.env['git.branch'].parse_git_url(self.remote_url)

    @api.depends('remote_url')
    def _compute_net_resources(self):
        for r in self:
            netloc = False
            netpath = False
            scheme = False
            if r.remote_url:
                url_parsed_data = r._parse_url()
                netloc = url_parsed_data.netloc
                netpath = url_parsed_data.path
                scheme = url_parsed_data.scheme
            r.netloc = netloc
            r.netpath = netpath
            r.scheme = scheme

    @api.depends('netloc')
    def compute_domain_name(self):
        for r in self:
            if r.netloc:
                r.domain_name = r.netloc.split('@')[-1]
            else:
                r.domain_name = False

    def get_default_branch(self):
        self.ensure_one()
        return self.env['git.branch'].search([('repository_id', '=', self.id), ('is_default', '=', True)], limit=1)

    def _compute_branches_count(self):
        branches_data = self.env['git.branch'].read_group([('repository_id', 'in', self.ids)], ['repository_id'], ['repository_id'])
        mapped_data = dict([(branch_dict['repository_id'][0], branch_dict['repository_id_count']) for branch_dict in branches_data])
        for r in self:
            r.branches_count = mapped_data.get(r.id, 0)

    @api.model
    def _guess_name_from_remote_url(self, remote_url):
        url_parsed_data = self.env['git.branch'].parse_git_url(remote_url)
        name = url_parsed_data.path
        if name.startswith('/'):
            name = name[1:]
        name = name.replace('/', '-')
        if name.endswith('.git'):
            name = name[:-4]
        return name

    @api.depends('remote_url')
    def _compute_name(self):
        for r in self:
            name = False
            if not r.name and r.remote_url:
                # Guess name from url
                name = r._guess_name_from_remote_url(r.remote_url)
            r.name = name

    def _get_repo_path(self):
        git_data_path = helper.git_data_path()
        for r in self:
            r.path = os.path.join(git_data_path, str(r.id), 'repo')

    def _Initialize(self):
        for r in self:
            repo = Repo.init(r.path, bare=True)
            repo.create_remote('origin', r.remote_url)

    def action_reinitialize(self):
        """
        This will delete all the git content from disk and Initialize the git repository at the path
        No Odoo record is touched here, just git content on disk
        """
        if not self.env.user.has_group('to_git.group_to_git_manager'):
            raise UserError(_("Access denied! Only Git Managers can reinitialize the git repository"))

        paths = self.mapped('path')
        for path in paths:
            parent_path = os.path.abspath(os.path.join(path, '..'))
            if os.path.exists(parent_path):
                shutil.rmtree(parent_path)
        self._Initialize()
        self.write({'with_credential': True})
        self._disable_auto_scan()

    def _disable_auto_scan(self):
        """
        This will disable auto scan for all the branches of the repo self
        """
        self.mapped('branch_ids').disable_auto_scan()

    @api.model_create_multi
    def create(self, vals_list):
        records = super(GitRepository, self).create(vals_list)
        records._Initialize()
        return records

    def write(self, vals):
        # force with_credential=True if remote_url is changed
        if 'remote_url' in vals:
            vals['with_credential'] = True
            # then set all related branches with auto_scan as False
            self._disable_auto_scan()

        result = super(GitRepository, self).write(vals)
        remote_url = vals.get('remote_url', False)
        if remote_url:
            for r in self:
                repo = Repo(r.path)
                repo.remote().set_url(remote_url)
        return result

    def unlink(self):
        paths = self.mapped('path')

        branch_ids = self.mapped('branch_ids')
        if branch_ids:
            branch_ids.unlink()

        result = super(GitRepository, self).unlink()
        for path in paths:
            parent_path = os.path.abspath(os.path.join(path, '..'))
            shutil.rmtree(parent_path)
        return result

    @helper.rerun_with_credentials
    def scan_for_branches(self):
        """
        Synchronize local branch list with the remote repository.
        """
        vals_list = []
        for r in self:
            branch_names, default_name = r._ls_remote()
            obsolete_branches = r.branch_ids.filtered(lambda b: b.name not in branch_names)
            if obsolete_branches:
                obsolete_branches.unlink()

            new_branch_names = [bname for bname in branch_names if bname not in r.branch_ids.mapped('name')]
            for name in new_branch_names:
                new_branch_data = {
                    'name': name,
                    'repository_id': r.id,
                    'is_default': name == default_name,
                    }
                vals_list.append(new_branch_data)

            # Update default branches
            for b in r.branch_ids:
                b.is_default = b.name == default_name

        new_branches = self.env['git.branch'].with_context(skip_check_branch_name=True).create(vals_list)
        return new_branches

    @helper.rerun_with_credentials
    def scan_for_branches_and_checkout(self):
        self.scan_for_branches()
        self.mapped('branch_ids').checkout()

    def action_pull(self):
        """
        Update all branches for latest changes from the remote.
        """
        return self.mapped('branch_ids').filtered(lambda b: b.checked_out).action_pull()

    def action_reset_to_head(self):
        """
        Reset all branches to their HEADs.
        """
        self.mapped('branch_ids').filtered(lambda b: b.checked_out).action_reset_to_head()

    def _get_git_env(self):
        """
        Returns environment variables for git.

        These environment variables contain credential info to authenticate
        git over SSH. And since we do not support interactive authentication,
        the returned environment variables also prevent git/ssh from asking
        for credentials if there are not any provided credentials or fail
        to authenticate with every provided credentials, which cause unwanted
        waiting on authentication.
        """
        self.ensure_one()
        private_keys = self._get_private_sshkeys_paths()
        # Since SSH client refuses keys that are too open in term of permission,
        # we need to chmod them to 600.
        for key in private_keys:
            os.chmod(key, stat.S_IREAD | stat.S_IWRITE)
        ssh_args = [
            '-oIdentitiesOnly=yes',
            '-oStrictHostKeyChecking=no',
            '-oBatchMode=yes',
            '-oConnectTimeout=5'
        ]
        for path in private_keys:
            ssh_args.append('-i"%s"' % path)
        if not private_keys:
            # If no keys are found for the user, disable public key authentication
            # to prevent ssh from using system keys (example: ~/.ssh/id_rsa)
            ssh_args.append('-oPubkeyAuthentication=no')
        git_ssh_cmd = 'ssh ' + ' '.join(ssh_args)
        return dict(GIT_SSH_COMMAND=git_ssh_cmd, GIT_ASKPASS='true')

    def _get_private_sshkeys_paths(self):
        self.ensure_one()
        return self.sudo().ssh_key_id.get_private_sshkeys_paths() or self.env.user.get_private_sshkeys_paths()

    def _ls_remote(self):
        """
        Return a tuple (list of branch names, default branch).
        """
        self.ensure_one()

        url = self.remote_url_with_credentials()
        try:
            out = Git(self.path).ls_remote(url, env=self._get_git_env())
        except GitCommandError as e:
            self.check_credentials()
            message = _('Failed to fetch data from the remote!\n'
                        'Please make sure that you have a working network connection, '
                        'the repository exists and you have the correct access rights.')
            if e.stderr:
                message += '\n' + e.stderr
            raise UserError(message)

        lines = out.splitlines()
        branch_refs = []
        head_ref_hash = None
        for line in lines:
            parts = line.split()
            ref_hash, ref_name = parts[0], parts[1]
            if ref_name.startswith('refs/heads/'):
                branch_name = ref_name[len('refs/heads/'):]
                branch_refs.append((branch_name, ref_hash))
            if ref_name == 'HEAD':
                head_ref_hash = ref_hash
        default_branch = None
        for branch_name, ref_hash in branch_refs:
            if ref_hash == head_ref_hash:
                default_branch = branch_name
        branch_names = [r[0] for r in branch_refs]
        return branch_names, default_branch

    def remote_url_with_credentials(self):
        """
        Return remote url with credentials extracted from context.
        """
        self.ensure_one()

        if not self.env.context.get('with_credential'):
            return self.remote_url

        username = self.env.context.get('username')
        password = self.env.context.get('password')
        credentials = ''
        if username:
            username = urllib.parse.quote(username)
            credentials += username
            if password:
                password = urllib.parse.quote(password)
                credentials += ':{}'.format(password)
        url_components = list(urllib.parse.urlparse(self.remote_url))
        netloc = url_components[1].rsplit('@')[-1]
        if credentials:
            netloc = '{}@{}'.format(credentials, netloc)
            url_components[1] = netloc
        return urllib.parse.urlunparse(url_components)

    def check_credentials(self):
        """
        Raise exception if there are not enough credentials in remote url.
        """
        self.ensure_one()

        # Stop checking if user submitted credentials.
        if self.env.context.get('with_credential'):
            return

        url_components = urllib.parse.urlparse(self.remote_url)
        if url_components.scheme.startswith('http'):
            if url_components.username and url_components.password:
                return
            username = url_components.username
            if username:
                username = urllib.parse.unquote(url_components.username)
            raise helper.MissingCredentialsError(username)

    def action_view_forks(self):
        self.ensure_one()
        child_ids = self.mapped('child_ids')
        action = self.env['ir.actions.act_window']._for_xml_id('to_git.git_repository_action')
        action['context'] = {'default_parent_id': self.id}
        # choose the view_mode accordingly
        modules_count = len(child_ids)
        if modules_count != 1:
            action['domain'] = "[('parent_id', 'in', " + str(self.ids) + ")]"
        elif modules_count == 1:
            res = self.env.ref('to_git.git_repository_view_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = child_ids.id
        return action
