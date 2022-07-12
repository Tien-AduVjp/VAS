from odoo import models, _
from odoo.exceptions import UserError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    def action_refuse(self):
        check_approval_request = self.filtered(lambda a: a.state in ('validate, done'))
        for approval in check_approval_request:
            if approval.sudo().overtime_plan_line_ids.payslip_ids.filtered(lambda p: p.state != 'draft'):
                raise UserError(_("You cannot refuse an approval request '%s' while it still has a reference to"
                                " the payslip '%s' which is not in draft status. Please have the payslip set to draft first.")
                                %(approval.display_name,
                                  approval.overtime_plan_line_ids.payslip_ids.filtered(lambda p: p.state != 'draft')[:1].display_name))
        return super(ApprovalRequest, self).action_refuse()

    def action_cancel(self):
        check_approval_request = self.filtered(lambda a: a.state in ('validate, done'))
        for approval in check_approval_request:
            if approval.sudo().overtime_plan_line_ids.payslip_ids.filtered(lambda p: p.state != 'draft'):
                raise UserError(_("You cannot cancel an approval request '%s' while it still has a reference to"
                                " the payslip '%s' which is not in draft status. Please have the payslip set to draft first.")
                                %(approval.display_name,
                                  approval.overtime_plan_line_ids.payslip_ids.filtered(lambda p: p.state != 'draft')[:1].display_name))
        return super(ApprovalRequest, self).action_cancel()
