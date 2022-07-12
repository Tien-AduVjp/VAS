from math import ceil

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    ave_daily_working_hours = fields.Float(string='Ave. Daily Working Hours', default=0.0,
                                           help="The average daily working hours of the equipment")

    working_hour_period = fields.Float(string='Working Hours between each preventive maintenance', default=0.0,
                                       help="The working hours of the equipment between each preventive maintenance")

    preventive_maintenance_mode = fields.Selection(selection_add=[('hour', 'By Hour')], ondelete={'hour': 'set default'})

    _sql_constraints = [
        ('ave_daily_working_hoursn_check',
         'CHECK(ave_daily_working_hours >= 0)',
         "Ave. Daily Working Hours must be greater than or equal to zero!"),

         ('working_hour_period_check',
         'CHECK(working_hour_period >= 0)',
         "Working Hours between each preventive maintenance must be greater than or equal to zero!"),
    ]

    @api.constrains('ave_daily_working_hours', 'working_hour_period', 'maintenance_team_id')
    def _check_maintenance_team_id(self):
        for r in self:
            if (r.ave_daily_working_hours != 0 or r.working_hour_period != 0) and not r.maintenance_team_id:
                raise ValidationError(_("Please select the maintenance team for the equipment '%s'") % r.display_name)

    @api.onchange('preventive_maintenance_mode', 'ave_daily_working_hours', 'working_hour_period')
    def _onchange_period_with_hour(self):
        if self.preventive_maintenance_mode == 'hour':
            self.period = self._calculate_period_with_hour()

    def _calculate_period_with_hour(self):
        self.ensure_one()
        if self.ave_daily_working_hours and self.working_hour_period:
            return ceil(self.working_hour_period / self.ave_daily_working_hours)
        return 0
