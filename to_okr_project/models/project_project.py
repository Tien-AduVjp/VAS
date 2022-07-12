from odoo import fields, models, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    okr_node_ids = fields.Many2many('okr.node', 'okr_node_project_rel', 'project_id', 'node_id', string="OKR", readonly=True,
                                    help="Store all the objectives and key results related to this project.")
    okr_nodes_count = fields.Integer('Project Task', compute='_compute_okr_nodes_count')
    
    def _compute_okr_nodes_count(self):
        for r in self:
            r.okr_nodes_count = len(r.okr_node_ids)
            
    def action_view_okr_nodes(self):
        action = self.env.ref('to_okr.okr_node_action')
        result = action.read()[0]
        result['domain'] = [('project_ids', 'in', self.ids)]
        return result
