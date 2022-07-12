from odoo import models, fields, _
from odoo.exceptions import ValidationError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'


    def _domain_equipment_id(self):
        if not self.user_has_groups('maintenance.group_equipment_manager'):
            return """
                ['|', '|',
                ('employee_id', '=', employee_id ),
                '&', ('department_id', '!=', False), ('department_id', '=', department_id),
                '&', ('employee_id', '=', False ), ('department_id', '=', False)]
            """
        return []

    maintenance_request_ids = fields.One2many('maintenance.request', 'approval_id', string='Maintenance Request')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', domain=_domain_equipment_id)
    maintenance_request_count = fields.Integer(string='Maintenance Request Count', compute='_compute_maintenance_request_count')

    def action_validate(self):
        for r in self:
            if r.type == 'maintenance_type' and not r.equipment_id:
                raise ValidationError(_("Equipment cannot be empty!"))
        return super(ApprovalRequest, self).action_validate()

    def _compute_maintenance_request_count(self):
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
