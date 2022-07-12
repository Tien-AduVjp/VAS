from odoo import models


class HrOvertimeRequestMassLine(models.TransientModel):
    _inherit = 'hr.overtime.request.mass.line'

    def _prepare_overtime_plan_vals(self):
        self.ensure_one()
        vals = super(HrOvertimeRequestMassLine, self)._prepare_overtime_plan_vals()
        vals.update({
            'approval_id': self._context.get('approval_request_id', False)
            })
        return vals
