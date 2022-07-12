from odoo import models
from odoo.tools import float_compare


class EquipmentWorkingFrequency(models.Model):
    _inherit = 'equipment.working.frequency'
    _description = 'Equipment Working Frequency'

    def _get_milestone_maintenance_days(self, milestone):
        self.ensure_one()
        if milestone.uom_id.category_id != self.working_uom_id.category_id:
            return 0
        if float_compare(self.total_working_amount, milestone.uom_id._compute_quantity(milestone.amount, self.working_uom_id) , precision_digits=0) == 1:
            return 0
        workload_per_hour = self.working_amount/self.period_time if self.period_time else 0
        if float_compare(workload_per_hour, 0, precision_digits=3) != 1:
            return 0
        milestone_amount = milestone.uom_id._compute_quantity(milestone.amount, self.working_uom_id)
        total_time = (milestone_amount - self.start_amount) / workload_per_hour
        total_day = self.equipment_id._get_total_working_day(total_time)
        return total_day
