from odoo import models, fields, _
from odoo.exceptions import ValidationError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'
    
    maintenance_request_ids = fields.One2many('maintenance.request', 'approval_id', string="Maintenance Request")
    equipment_id = fields.Many2one('maintenance.equipment', string="Equipment")
    maintenance_request_count = fields.Integer(string="Maintenance Request Count", compute='_compute_request_count')
    
    def action_validate(self):
        if self.type == 'maintenance_type' and not self.equipment_id:
            raise ValidationError(_("Equipment cannot be empty!"))
        super(ApprovalRequest, self).action_validate()
        
    def _compute_request_count(self):
        for r in self:
            r.maintenance_request_count = len(r.maintenance_request_ids)
            
    def action_view_maintenance_request(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Requests',
            'view_mode': 'tree,form',
            'res_model': 'maintenance.request',
            'target': 'current',
            'domain': [('approval_id', '=', self.id)]
            }
        return action