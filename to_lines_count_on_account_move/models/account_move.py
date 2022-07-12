from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    lines_count = fields.Integer(string='Journal Items Count', compute='_compute_lines_count', store=True)
    
    @api.depends('line_ids')
    def _compute_lines_count(self):
        for r in self:
            r.lines_count = len(r.line_ids)