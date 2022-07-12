from odoo import fields, models


class MrpEcoApprovalTemplate(models.Model):
    _name = "mrp.eco.approval.template"
    _description="ECO Approval Template"
    _order = "sequence"

    name = fields.Char(string='Role', required=True)
    sequence = fields.Integer(string='Sequence')
    approval_type = fields.Selection([
        ('optional', 'The approval is optional'),
        ('mandatory', 'Required to approve'),
        ('comment', 'Comments only')], 
        string='Approval Type', default='mandatory', required=True)
    user_ids = fields.Many2many('res.users', string='Users', required=True)
    stage_id = fields.Many2one('mrp.eco.stage', string='Stage', required=True)
