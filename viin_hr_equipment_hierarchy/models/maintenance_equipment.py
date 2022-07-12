from odoo import models, fields, api


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    equipment_assign_to = fields.Selection(compute='_compute_equipment_assign_to', store=True, readonly=False)
    owner_user_id = fields.Many2one(compute='_compute_owner', store=True)
    assign_date = fields.Date(compute='_compute_equipment_assign', store=True, readonly=False, copy=True)

    @api.depends('parent_id.equipment_assign_to')
    def _compute_equipment_assign_to(self):
        for r in self:
            if r.parent_id:
                r.equipment_assign_to = r.parent_id.equipment_assign_to
            else:
                r.equipment_assign_to = r.equipment_assign_to

    @api.depends('employee_id', 'department_id', 'equipment_assign_to', 'parent_id.owner_user_id')
    def _compute_owner(self):
        for r in self:
            r.owner_user_id = self.env.user.id
            if r.parent_id:
                r.owner_user_id = r.parent_id.owner_user_id.id
            elif r.equipment_assign_to == 'employee':
                r.owner_user_id = r.employee_id.user_id.id
            elif r.equipment_assign_to == 'department':
                r.owner_user_id = r.department_id.manager_id.user_id.id

    @api.depends('equipment_assign_to', 'parent_id.assign_date', 'parent_id.employee_id', 'parent_id.department_id')
    def _compute_equipment_assign(self):
        for r in self:
            if r.parent_id:
                r.department_id = r.parent_id.department_id
                r.employee_id = r.parent_id.employee_id
                r.assign_date = r.parent_id.assign_date
                continue
            elif r.equipment_assign_to == 'employee':
                r.department_id = False
                r.employee_id = r.employee_id
            elif r.equipment_assign_to == 'department':
                r.employee_id = False
                r.department_id = r.department_id
            else:
                r.department_id = r.department_id
                r.employee_id = r.employee_id
            r.assign_date = fields.Date.context_today(self)
