from odoo import models, fields, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    manager_ids = fields.One2many('hr.employee', string='Superiors', compute='_compute_managers',
                                  help="Direct and indirect managers", compute_sudo=True)
    recursive_child_ids = fields.Many2many('hr.department', 'parent_id', 'child_id', compute='_compute_recursive_child_ids',
                                           compute_sudo=True, string='Recursive Child Departments',
                                           help="Direct and Indirect Child Departments")
    name = fields.Char(translate=True)

    def name_get(self):
        result = []
        if self.env.context.get('hierarchical_naming', True):
            for r in self:
                name = r._get_hierarchical_name()
                result.append((r.id, name))
            return result
        return super(HrDepartment, self).name_get()

    @api.depends('parent_id', 'manager_id', 'parent_id.manager_id')
    def _compute_managers(self):
        for r in self:
            r.manager_ids = r._get_recursive_managers()

    @api.depends('child_ids', 'child_ids.child_ids')
    def _compute_recursive_child_ids(self):
        for r in self:
            r.recursive_child_ids = r._get_recursive_children()

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        records = super(HrDepartment, self).create(vals_list)
        # as Odoo caches ir.rules's result for performance,
        # clearing cache when creating new department that may modify
        # current employee hierarchy is required
        self.env['ir.rule'].clear_caches()
        return records

    def write(self, vals):
        res = super(HrDepartment, self).write(vals)
        # as Odoo caches ir.rules's result for performance,
        # clearing cache when modifying department that may modify
        # current employee hierarchy is required
        if 'manager_id' in vals or 'parent_id' in vals:
            self.env['ir.rule'].clear_caches()
        return res

    def unlink(self):
        res = super(HrDepartment, self).unlink()
        # as Odoo caches ir.rules's result for performance,
        # clearing cache when unlink department that may modify
        # current employee hierarchy is required
        self.env['ir.rule'].clear_caches()
        return res

    def _get_recursive_managers(self):
        managers = self.manager_id
        for parent in self.parent_id:
            managers |= parent._get_recursive_managers()
        return managers

    def _get_recursive_children(self):
        children = self.child_ids
        for child in self.child_ids:
            children |= child._get_recursive_children()
        return children

    def _get_hierarchical_name(self):
        """method to form the name of the department hierarchically. E.g. `Parent / Child / Sub-Child`"""
        if not self.parent_id:
            return self.name
        else:
            return '%s / %s' % (self.parent_id._get_hierarchical_name(), self.name)
