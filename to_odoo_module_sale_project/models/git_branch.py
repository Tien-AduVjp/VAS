from odoo import models


class GitBranch(models.Model):
    _inherit = 'git.branch'

    def _parse_manifest(self, manifest_file_name, available_license_versions):
        """
        If the manifest has task_ids key, we parse it and mapped with existing project.task record
        """

        def clean_task_id(task_id):
            if isinstance(task_id, str):
                task_id = it.strip()
                if task_id.isdigit():
                    task_id = int(task_id)
            return task_id

        vals = super(GitBranch, self)._parse_manifest(manifest_file_name, available_license_versions)

        if 'task_ids' in vals:
            final_task_ids = []
            task_ids = vals['task_ids']
            if isinstance(vals['task_ids'], str):
                task_ids = task_ids.split(',')

            if isinstance(task_ids, list) or isinstance(task_ids, tuple):
                for it in task_ids:
                    task_id = clean_task_id(it)
                    if isinstance(task_id, int):
                        final_task_ids.append(task_id)

            # search to ensure task_ids exist in database
            final_task_ids = self.env['project.task'].search([('id', 'in', final_task_ids)])
            if final_task_ids:
                # replace the relation
                vals['task_ids'] = [(6, 0, final_task_ids.ids)]
            else:
                # no existing task found corresponding to the definitions in the manifest, just remove from vals
                vals.pop('task_ids', None)
        return vals

