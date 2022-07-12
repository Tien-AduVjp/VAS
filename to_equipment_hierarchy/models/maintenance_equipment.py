from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    parent_id = fields.Many2one('maintenance.equipment', string='Directly apart of', ondelete='cascade', help="This field is to indicate"
                                " that this equipment is directly apart of another equipment",
                                tracking=True)
    child_ids = fields.One2many('maintenance.equipment', 'parent_id', string="Parts", help="Equipments that are directly apart of this equipment,"
                                " not including parts of parts")

    # recursive childs and parents
    recursive_child_ids = fields.Many2many('maintenance.equipment', 'recursive_equipment_children', 'parent_id', 'child_id', string='Recursive Parts',
                                           compute='_compute_recursive_child_ids', store=True,
                                           help="Equipments that are recursively apart of this equipments. For example, parts of parts")
    recursive_parent_ids = fields.Many2many('maintenance.equipment', 'recursive_equipment_children', 'child_id', 'parent_id', string='Also apart of',
                                            compute='_compute_recursive_parent_ids',
                                            help="This field is to indicate that this equipment is apart of other equipments. For example,"
                                            " a cylinder is apart of its engine assembled in a car")

    # recursive maintenances
    child_maintenance_ids = fields.Many2many('maintenance.request', 'child_equipment_maintenance', 'equipment_id', 'maintenance_id',
                                             string='Parts Only Maintenances',
                                             compute='_compute_child_maintenance_ids', store=True,
                                             help="Maintenances of the equipment parts only, which does not include the maintenance of the current equipment")
    child_maintenances_count = fields.Integer(string='Parts Maintenances Count', compute='_compute_child_maintenances_count', store=True)
    child_maintenances_open_count = fields.Integer(string='Parts Current Maintenances Count', compute='_compute_child_maintenances_count', store=True)

    recursive_maintenance_ids = fields.Many2many('maintenance.request', 'recursive_equipment_maintenance', 'equipment_id', 'maintenance_id',
                                                compute='_compute_recursive_maintenance_ids', string='All Maintenances', store=True,
                                                help="All the maintenances of this equipment and its parts")

    recursive_maintenances_count = fields.Integer(string='Maintenances', compute='_compute_recursive_maintenances_count', store=True)
    recursive_maintenances_open_count = fields.Integer(string='Current Maintenances', compute='_compute_recursive_maintenances_count', store=True)

    # synch with parents
    # assign_date = fields.Date(compute='_compute_assign_date', readonly=False, store=True) TODO: Reprocess the code or remove it when upgrading 14
    # owner_user_id = fields.Many2one(compute='_synch_owner_user_with_parent', readonly=False, store=True) TODO: Reprocess the code or remove it when upgrading 14
    location = fields.Char(compute='_compute_location', readonly=False, store=True)

    def _get_nested_childdren(self):
        child_ids = self.mapped('child_ids')
        for child_id in child_ids:
            child_ids |= child_id._get_nested_childdren()
        return child_ids
    
    def _get_recursive_parents(self):
        parents = self.parent_id
        for parent in parents:
            parents |= parent._get_recursive_parents()
        return parents

    @api.depends('child_ids', 'child_ids.recursive_child_ids')
    def _compute_recursive_child_ids(self):
        for r in self:
            r.recursive_child_ids = r._get_nested_childdren()
    
    @api.depends('parent_id', 'parent_id.recursive_parent_ids')
    def _compute_recursive_parent_ids(self):
        for r in self:
            r.recursive_parent_ids = r._get_recursive_parents()

    @api.constrains('parent_id', 'location')
    def _check_location_synch(self):
        for r in self:
            if r.location and r.parent_id.location and r.location != r.parent_id.location:
                raise UserError(_("It is impossible for the part '%s' to be put in a location other than the location of its parent ('%s')'s location"))


    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive region.'))
        return True

    #TODO: Reprocess the code or remove it when upgrading 14
    # @api.depends('parent_id.assign_date')
    # def _compute_assign_date(self):
    #     for r in self:
    #         if r.parent_id.assign_date:
    #                 r.assign_date = r.parent_id.assign_date
                    
    # TODO: Reprocess the code or remove it when upgrading 14
    # @api.depends('parent_id.owner_user_id')
    # def _synch_owner_user_with_parent(self):
    #     for r in self:
    #         if r.parent_id.owner_user_id:
    #             r.owner_user_id = r.parent_id.owner_user_id
    
    @api.depends('employee_id', 'department_id', 'equipment_assign_to', 'parent_id.owner_user_id')
    def _compute_owner(self):
        super(MaintenanceEquipment, self)._compute_owner()
        for r in self:
            if r.parent_id.owner_user_id:
                r.owner_user_id = r.parent_id.owner_user_id
            else:
                r.owner_user_id = r.owner_user_id

    @api.depends('parent_id.location')
    def _compute_location(self):
        for r in self:
            if r.parent_id.location:
                r.location = r.parent_id.location
            else:
                r.location = r.location

    @api.depends('recursive_child_ids', 'recursive_child_ids.maintenance_ids')
    def _compute_child_maintenance_ids(self):
        for r in self:
            r.child_maintenance_ids = r.recursive_child_ids.mapped('maintenance_ids')

    @api.depends('maintenance_ids', 'child_maintenance_ids')
    def _compute_recursive_maintenance_ids(self):
        for r in self:
            r.recursive_maintenance_ids = r.maintenance_ids + r.child_maintenance_ids

    @api.depends('child_maintenance_ids', 'child_maintenance_ids.stage_id.done')
    def _compute_child_maintenances_count(self):
        for r in self:
            r.child_maintenances_count = len(r.child_maintenance_ids)
            r.child_maintenances_open_count = len(r.child_maintenance_ids.filtered(lambda x: not x.stage_id.done))

    @api.depends('recursive_maintenance_ids', 'recursive_maintenance_ids.stage_id.done')
    def _compute_recursive_maintenances_count(self):
        for r in self:
            r.recursive_maintenances_count = len(r.recursive_maintenance_ids)
            r.recursive_maintenances_open_count = len(r.recursive_maintenance_ids.filtered(lambda x: not x.stage_id.done))
    
    @api.onchange('equipment_assign_to', 'parent_id')
    def _onchange_equipment_assign_to(self):
        super(MaintenanceEquipment, self)._onchange_equipment_assign_to()
        if self.parent_id:
            self.assign_date = self.parent_id.assign_date

    def action_view_recursive_maintenances(self):
        recursive_maintenance_ids = self.mapped('recursive_maintenance_ids')
        action = self.env.ref('maintenance.hr_equipment_request_action_from_equipment')
        result = action.read()[0]
        result['domain'] = "[('id','in',%s)]" % (recursive_maintenance_ids.ids)
        return result

    def action_view_child_maintenances(self):
        child_maintenance_ids = self.mapped('child_maintenance_ids')
        action = self.env.ref('maintenance.hr_equipment_request_action_from_equipment')
        result = action.read()[0]
        result['domain'] = "[('id','in',%s)]" % (child_maintenance_ids.ids)
        return result
    
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        rec = super(MaintenanceEquipment, self).create(vals_list)
        for super_parent in rec.filtered(lambda r: not r.parent_id):
            super_parent.recursive_child_ids.write({'assign_date': super_parent.assign_date})
        return rec
    
    def write(self, vals):
        update_children_assign_date = 'assign_date' in vals and not self._context.get('ignore_update_children_assign_date')
        res = super(MaintenanceEquipment, self).write(vals)
        if update_children_assign_date:
            (self.recursive_child_ids - self).with_context(ignore_update_children_assign_date=True).write({'assign_date': vals.get('assign_date', False)})
        return res
