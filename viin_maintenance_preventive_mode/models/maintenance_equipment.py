from odoo import fields, models, api


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    preventive_maintenance_mode = fields.Selection([('default', 'By Default')], string='Preventive Maintenance Mode',
                                                   default='default', required=True)

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        res = super(MaintenanceEquipment, self).create(vals_list)
        if not res._context.get('skip_calculate_period', False):
            res._calculate_period()
        return res

    def write(self, vals):
        res = super(MaintenanceEquipment, self).write(vals)
        if not self._context.get('skip_calculate_period', False):
            self._calculate_period()
        return res

    def _calculate_period(self):
        """This method recalculates the period of the equipment.
        Methods that should be added in an preventive_maintenance_mode-specific implementation:
        - ``_calculate_period_with_<preventive_maintenance_mode>(self)`` to return period value"""
        # period is non-computed field, because to avoid dead test of Odoo
        for r in self:
            custom_method_name = '_calculate_period_with_%s' % r.preventive_maintenance_mode
            if hasattr(r, custom_method_name):
                r = r.with_context(skip_calculate_period=True)
                r.period = getattr(r, custom_method_name)()
