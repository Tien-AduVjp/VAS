from odoo import models, api
from odoo.tools import float_compare

class EquipmentWorkingFrequency(models.Model):
    _inherit = 'equipment.working.frequency'
    _description = 'Equipment Working Frequency'
    
    @api.model
    def _get_milestone_maintenance_days(self, milestone):
        # get maintenance date based on total working amount, working frequency and milestone's amount
        if milestone.uom_id.category_id != self.working_uom_id.category_id:
            return 0
        if float_compare(self.total_working_amount, milestone.uom_id._compute_quantity(milestone.amount, self.working_uom_id) , precision_digits=0) == 1:
            return 0
        day_uom = self.env.ref('uom.product_uom_day')
        period_time = self.period_time_uom_id._compute_quantity(self.period_time, day_uom)
        day_amount = self.working_amount/period_time if period_time else 0
        if float_compare(day_amount, 0, precision_digits=3) != 1:
            return 0
        return round((milestone.uom_id._compute_quantity(milestone.amount, self.working_uom_id) -  self.total_working_amount)/day_amount)
        
        
