from odoo import models, _
from odoo.exceptions import UserError


class HrOvertimePlan(models.Model):
    _inherit = 'hr.overtime.plan'

    def action_resolve_contract_mismatch(self):
        for ot_line in self.line_ids:
            if ot_line.has_non_draft_payslips:
                raise UserError(_("You may not be able to resolve mismatch contract while overtime plan line %s still referred by"
                                  " the payslip '%s' which is not in draft state. Please have the payslip set to draft first.")
                                  % (ot_line.display_name, ot_line.sudo().payslip_ids.filtered(lambda sl: sl.state != 'draft')[:1].display_name))
        return super(HrOvertimePlan, self).action_resolve_contract_mismatch()
