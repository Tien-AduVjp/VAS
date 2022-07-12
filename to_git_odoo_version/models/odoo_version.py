from odoo import models, fields, api


class OdooVersion(models.Model):
    _inherit = 'odoo.version'

    git_branch_ids = fields.One2many('git.branch', 'odoo_version_id', string='Git Branches', readonly=True,
                                     help="Related Git Branches that have the same name as this Odoo version's")
    git_branches_count = fields.Integer(string='Git Branches Count', compute='_compute_git_branches_count')

    def _compute_git_branches_count(self):
        branches_data = self.env['git.branch'].read_group([('odoo_version_id', 'in', self.ids)], ['odoo_version_id'], ['odoo_version_id'])
        mapped_data = dict([(item['odoo_version_id'][0], item['odoo_version_id_count']) for item in branches_data])
        for r in self:
            r.git_branches_count = mapped_data.get(r.id, 0)

    def action_view_git_branches(self):
        git_branch_ids = self.mapped('git_branch_ids')
        action = self.env.ref('to_git.git_branch_action_window')
        result = action.read()[0]

        # choose the view_mode accordingly
        branches_count = len(git_branch_ids)
        if branches_count != 1:
            result['domain'] = "[('odoo_version_id', 'in', " + str(self.ids) + ")]"
        elif branches_count == 1:
            res = self.env.ref('to_git_odoo_version.git_branch_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = git_branch_ids.id
        return result

    def _get_branch_model(self, sudo_if_required=True):
        Branch = self.env['git.branch']
        if not self.env.user.has_group('to_git.group_to_git_user') and sudo_if_required:
            Branch = Branch.sudo()
        return Branch

    def _map_branches(self):
        Branch = self._get_branch_model()
        for r in self:
            branch_ids = Branch.search([('odoo_version_id', '=', False), ('name', '=', r.name)])
            if branch_ids:
                branch_ids.write({
                    'odoo_version_id': r.id
                    })
        return True

    @api.model
    def create(self, vals):
        res = super(OdooVersion, self).create(vals)
        if 'name' in vals:
            res._map_branches()
        return res

    def write(self, vals):
        if 'name' in vals:
            # version name is changed, remove the relation with the branches to remap later
            Branch = self._get_branch_model()
            for r in self:
                branch_ids = Branch.search([('odoo_version_id', '=', r.id)])
                if branch_ids:
                    branch_ids.write({
                        'odoo_version_id': False
                        })
        res = super(OdooVersion, self).write(vals)
        if 'name' in vals:
            # remap branches
            self._map_branches()
        return res

