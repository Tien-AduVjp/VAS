from odoo import models


class HrOvertimeRequestMassLine(models.TransientModel):
    _inherit = 'hr.overtime.request.mass.line'

    def _prepare_overtime_plan_vals(self):
        self.ensure_one()
        vals = super(HrOvertimeRequestMassLine, self)._prepare_overtime_plan_vals()
        vals.update({
            'for_project_id': self.overtime_request_mass_id.for_project_id.id
            })
        return vals
