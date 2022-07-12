from odoo import api, fields, models


class MrpEcoApproval(models.Model):
    _name = "mrp.eco.approval"
    _description="ECO Approval"

    eco_id = fields.Many2one('mrp.eco', ondelete='cascade', string='ECO', required=True)
    approval_template_id = fields.Many2one('mrp.eco.approval.template', ondelete='cascade', string='Template', required=True)
    name = fields.Char(string='Role', related='approval_template_id.name', store=True)
    user_id = fields.Many2one('res.users', string='Approved by')
    required_user_ids = fields.Many2many('res.users', string='Requested Users', related='approval_template_id.user_ids')
    template_stage_id = fields.Many2one('mrp.eco.stage', string='Approval Stage', related='approval_template_id.stage_id', store=True)
    eco_stage_id = fields.Many2one('mrp.eco.stage', string='ECO Stage', related='eco_id.stage_id', store=True)
    status = fields.Selection([
        ('none', 'Not Yet'),
        ('comment', 'Commented'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], string='Status', default='none', required=True)
    is_approved = fields.Boolean(string="Is Approved", compute='_compute_is_approved', store=True)
    is_rejected = fields.Boolean(string="Is Rejected", compute='_compute_is_rejected', store=True)

    @api.depends('status', 'approval_template_id.approval_type')
    def _compute_is_approved(self):
        for r in self:
            if r.approval_template_id.approval_type == 'mandatory':
                r.is_approved = r.status == 'approved'
            else:
                r.is_approved = True

    @api.depends('status', 'approval_template_id.approval_type')
    def _compute_is_rejected(self):
        for r in self:
            if r.approval_template_id.approval_type == 'mandatory':
                r.is_rejected = r.status == 'rejected'
            else:
                r.is_rejected = False
