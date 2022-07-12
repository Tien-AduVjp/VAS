from odoo import models, fields
from odoo.exceptions import ValidationError


class CheckoutCommitWizard(models.TransientModel):
    _name = 'git.branch.checkout_commit'
    _description = 'Checkout a Commit Wizard'

    def _get_recent_commits(self):
        branch_id = self._context.get('active_id')
        branch = self.env['git.branch'].browse(branch_id)
        return branch.recent_commits()

    def _get_detached_head_state(self):
        branch_id = self._context.get('active_id')
        branch = self.env['git.branch'].browse(branch_id)
        return branch.detached_head

    commit_hash = fields.Char(string='Commit Hash', help='SHA-1 checksum of a commit, in abbreviated or full form')
    recent_commits = fields.Many2many('git.commit', default=_get_recent_commits, help='List of recent commits')
    detached_head = fields.Boolean(string='Detached HEAD', default=_get_detached_head_state, readonly=True)

    def select(self):
        if self._context.get('from_list'):
            commit_id = self._context.get('active_id')
            commit_hash = self.env['git.commit'].browse(commit_id).hash
        else:
            commit_hash = self.commit_hash
            if isinstance(commit_hash, str):
                commit_hash = commit_hash.strip()
            if not commit_hash:
                raise ValidationError('Commit Hash is empty!')

        branch_id = self._context.get('branch_id')
        branch = self.env['git.branch'].browse(branch_id)
        branch.checkout_commit(commit_hash)

    def reset(self):
        branch_id = self._context.get('branch_id')
        branch = self.env['git.branch'].browse(branch_id)
        branch.reset_head()
