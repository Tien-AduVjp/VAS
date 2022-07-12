from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .. import helper


class WizardGitURLAdd(models.TransientModel):
    _name = 'wizard.git.url.add'
    _description = 'Git URL Adding Wizard'

    url = fields.Char(string='Git URL', required=True, help="The provided url should follow a standardized format:"
                      " ssh://git@github.com/odoo/odoo.git#git_branch_name. The url of your repository might then be modified"
                      " in order to respect this standard.")
    git_repo_remote_url = fields.Char(compute='_compute_git_repo_url')
    git_net_path = fields.Char(string='Net Path', compute='_compute_git_repo_url', help="The path of the resource. For example, '/odoo/odoo'.")
    git_branch_name = fields.Char(compute='_compute_git_repo_url')
    vendor_id = fields.Many2one('res.partner', string='Vendor', help="The partner who holds the copyright of this repository."
                                " Leave it empty if this is a repository of your company's.")
    checkout = fields.Boolean(string='Immediate Checkout', help="If enabled, the git branch specified in the URL will be checkout"
                              " immediately.")

    @api.constrains('url')
    def _check_url(self):
        for r in self:
            url_parsed_data = r._parse_url()
            if not url_parsed_data.scheme:
                raise UserError(_("No scheme found in your given URL. You must specify either HTTP/HTTPs or SSH scheme."))
            elif url_parsed_data.scheme not in ('ssh', 'http', 'https'):
                raise UserError(_("The scheme %s is not supported. Please use either HTTP/HTTPS or SSH.") % url_parsed_data.scheme)

            if not url_parsed_data.netloc:
                raise UserError(_("No Net Location found in your given URL. A net location should follow a standardized"
                                  " format: git@github.com, where `git` is the user who has access to the git repository"
                                  " and `github.com` is a domain to what your git repo belongs."))
            if not url_parsed_data.path:
                raise UserError(_("No netpath found in your given URL. A netpath is a path of an URL appending to the domain"
                                  " name of the URL. For example: '/odoo/odoo.git' is the netpath of the URL"
                                  " 'ssh://git@github.com/odoo/odoo.git#8.0'."))
            if not url_parsed_data.fragment:
                raise UserError(_("No git branch found in your URL. You must specify a git branch after the # letter in"
                                  " the URL. For example: ssh://git@github.com/odoo/odoo.git#git_branch_name."))
            if url_parsed_data.params or url_parsed_data.query:
                raise UserError(_("You should not give any param or query in your URL. Please follow a standardized format:"
                                  " ssh://git@github.com/odoo/odoo.git#git_branch_name."))

    def _parse_url(self):
        self.ensure_one()
        return self.env['git.branch'].parse_git_url(self.url)

    def _compute_git_repo_url(self):
        for r in self:
            url_parsed_data = r._parse_url()
            r.git_repo_remote_url = '%s://%s%s' % (url_parsed_data.scheme, url_parsed_data.netloc, url_parsed_data.path)
            r.git_net_path = url_parsed_data.path
            r.git_branch_name = url_parsed_data.fragment

    def _prepare_git_repo_data(self):
        return {
            'remote_url': self.git_repo_remote_url,
            'name': self.env['git.repository']._guess_name_from_remote_url(self.git_repo_remote_url),
            'vendor_id': self.vendor_id and self.vendor_id.id or False
            }

    def _prepare_git_branch_data(self, repository):
        return {
            'name': self.git_branch_name,
            'repository_id': repository.id,
            }

    @helper.rerun_with_credentials
    def add(self):
        GitRepo = self.env['git.repository']
        GitBranches = self.env['git.branch']
        self.ensure_one()
        netpaths_to_search = []
        if self.git_net_path:
            netpaths_to_search.append(self.git_net_path)
            if self.git_net_path.endswith('.git'):
                netpaths_to_search.append(self.git_net_path[:-4])
            else:
                netpaths_to_search.append(self.git_net_path + '.git')
        repo = GitRepo.search([('netpath', 'in', netpaths_to_search)], limit=1)
        if not repo:
            repo = GitRepo.create(self._prepare_git_repo_data())
        branch = GitBranches.search([('repository_id', '=', repo.id), ('name', '=', self.git_branch_name)], limit=1)
        if not branch:
            branch = GitBranches.create(self._prepare_git_branch_data(repo))

        if self.checkout and not branch.checked_out:
            branch.checkout()

        return branch

