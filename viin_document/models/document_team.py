from odoo import fields, models

class DocumentTeam(models.Model):
    _name = 'document.team'
    _description = "Document Team"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    leader_id= fields.Many2one('res.users', string='Leader', required=True, tracking=True, check_company=True)
    description = fields.Text(string='Description')
    member_ids = fields.Many2many('res.users', string='Members')
    count_member = fields.Integer(string='Members Count', compute='_compute_total_member')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    active = fields.Boolean(string='Active', default=True)

    def _compute_total_member(self):
        for r in self:
            r.count_member = len(r.member_ids)
