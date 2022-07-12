from odoo import models, api


class HolidaysType(models.Model):
    _inherit = 'hr.leave.type'

    @api.onchange('allocation_type')
    def _onchange_allocation_type(self):
        if self.allocation_type == 'fixed_allocation':
            if self._origin and self._origin.allocation_type == 'fixed_allocation':
                self.allocation_validation_type = self._origin.allocation_validation_type
            else:
                self.allocation_validation_type = 'manager'
        else:
            self.allocation_validation_type = False
