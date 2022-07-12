from odoo import models, fields


class GitCommit(models.TransientModel):
    _name = 'git.commit'
    _description = 'Git Commit'

    name = fields.Char(compute='_compute_name')
    hash = fields.Char(required=True)
    message = fields.Text(required=True)

    def _compute_name(self):
        for record in self:
            record.name = record.message.splitlines()[0]
