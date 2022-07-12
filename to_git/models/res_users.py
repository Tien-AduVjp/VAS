from odoo import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _personal_sshkeys_only(self):
        if not self.has_group('to_git.group_to_git_manager') and super(ResUsers, self)._personal_sshkeys_only():
            return True
        return False
