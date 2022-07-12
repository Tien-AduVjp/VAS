from odoo import models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def write(self, vals):
        """
        This override make sure internal users who have read access to a project task can always change its kanban state
        """
        if 'kanban_state' in vals and len(vals) == 1 and self.env.user.has_group('base.group_user') and self.check_access_rights('read'):
            apply_sudo = False
            self.check_access_rule('read')
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except Exception:
                apply_sudo = True
            if apply_sudo:
                self = self.sudo()
        return super(ProjectTask, self).write(vals)
