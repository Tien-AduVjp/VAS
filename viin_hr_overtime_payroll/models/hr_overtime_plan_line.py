from odoo import models, fields, _
from odoo.exceptions import UserError


class HrOvertimePlanLine(models.Model):
    _inherit = 'hr.overtime.plan.line'

    payslip_ids = fields.Many2many('hr.payslip', 'overtime_plan_line_hr_payslip_rel', 'plan_line_id', 'payslip_id',
                                   string='Pay Slips', readonly=True,
                                   help="The payslips that take care of this entry")

    def unlink(self):
        for r in self.filtered(lambda l: l.has_non_draft_payslips):
            raise UserError(_("You may not be able to delete the overtime plan line %s while it is still referred by"
                              " the payslip '%s' which is not in draft state. Please have the payslip set to draft first.")
                              % (r.display_name, r.sudo().payslip_ids.filtered(lambda sl: sl.state != 'draft')[:1].display_name))
        return super(HrOvertimePlanLine, self).unlink()

    def _compute_has_non_draft_payslips(self):
        super(HrOvertimePlanLine, self)._compute_has_non_draft_payslips()
        for r in self.filtered(lambda l: any(payslip.state != 'draft' for payslip in l.payslip_ids)):
            r.has_non_draft_payslips = True
