from odoo import models, _
from odoo.exceptions import UserError


class HrOvertimePlan(models.Model):
    _inherit = 'hr.overtime.plan'

    def action_cancel(self):
        check_overtime_plans = self.filtered(lambda o: o.state and o.state in ('validate, done'))
        for plan in check_overtime_plans:
            if plan.sudo().line_ids.payslip_ids.filtered(lambda p: p.state != 'draft'):
                raise UserError(_("You cannot cancel an overtime plan '%s' while it still has a reference to"
                                " the payslip '%s' which is not in draft status. Please have the payslip set to draft first.")
                                %(plan.display_name,
                                  plan.line_ids.payslip_ids.filtered(lambda p: p.state != 'draft')[:1].display_name))
        return super(HrOvertimePlan, self).action_cancel()

    def action_refuse(self):
        check_overtime_plans = self.filtered(lambda o: o.state and o.state in ('validate, done'))
        for plan in check_overtime_plans:
            if plan.sudo().line_ids.payslip_ids.filtered(lambda p: p.state != 'draft'):
                raise UserError(_("You cannot refuse an overtime plan '%s' while it still has a reference to"
                                " the payslip '%s' which is not in draft status. Please have the payslip set to draft first.")
                                %(plan.display_name,
                                  plan.line_ids.payslip_ids.filtered(lambda p: p.state != 'draft')[:1].display_name))
        return super(HrOvertimePlan, self).action_refuse()
