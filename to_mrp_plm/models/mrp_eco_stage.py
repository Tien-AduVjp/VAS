from odoo import api, fields, models


class MrpEcoStage(models.Model):
    _name = 'mrp.eco.stage'
    _description = 'Engineering Change Order Stage'
    _order = "sequence, id"
    _fold_name = 'folded'

    name = fields.Char(string='Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=0)
    folded = fields.Boolean(string='Folded in kanban view')
    is_final_stage = fields.Boolean(string='Final Stage')
    allow_apply_change = fields.Boolean(string='Allow Apply Change')
    type_ids = fields.Many2many('mrp.eco.type', string='ECO Types', required=True)
    approval_template_ids = fields.One2many('mrp.eco.approval.template', 'stage_id', string='Approvals')
    approval_roles = fields.Char(string='Approval Roles', compute='_compute_approvals', store=True)
    is_blocking = fields.Boolean(string='Blocking Stage', compute='_compute_is_blocking', store=True)

    @api.depends('approval_template_ids.name')
    def _compute_approvals(self):
        for r in self:
            template_names = r.approval_template_ids.mapped('name')
            r.approval_roles = ', '.join(template_names)

    @api.depends('approval_template_ids.approval_type')
    def _compute_is_blocking(self):
        for r in self:
            blocking = False
            for template in r.approval_template_ids:
                if template.approval_type == 'mandatory':
                    blocking = True
                    break
            r.is_blocking = blocking
