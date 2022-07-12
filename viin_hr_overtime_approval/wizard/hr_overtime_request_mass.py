from odoo import models, fields, _
from odoo.exceptions import ValidationError


class HrOvertimeRequestMass(models.TransientModel):
    _inherit = 'hr.overtime.request.mass'

    approval_required = fields.Boolean(string='Approval Required', default=True, groups="viin_hr_overtime.group_overtime_officer")
    approval_id = fields.Many2one('approval.request', string='Approval Request', domain="[('type','=','overtime'),('company_id','in',company_ids)]")

    def _prepare_approval_request_vals(self):
        self.ensure_one()
        approval_type = self.env['approval.request.type'].search([
            ('company_id', '=', self.env.company.id),
            ('type', '=', 'overtime')
            ], limit=1)
        if not approval_type:
            raise ValidationError(_("No overtime approval request type available for the company `%s`."
                                    " Upgrading the module `viin_hr_overtime_approval` may solve this problem.")
                                    % self.env.company.display_name
                                    )
        return {
            'title': _("Overtime Approval Request"),
            'employee_id': self.env.user.employee_id.id,
            'approval_type_id': approval_type.id,
            'currency_id': self.env.company.currency_id.id,
            'deadline': approval_type._get_deadline()
            }

    def _generate_approval_request(self):
        self.ensure_one()
        request = self.env['approval.request'].create(self._prepare_approval_request_vals())
        self.approval_id = request
        return request

    def action_schedule(self):
        self.ensure_one()
        approval_required = self.sudo().approval_required
        if approval_required:
            approval_request = self.approval_id or self._generate_approval_request()
            self = self.with_context(approval_request_id=approval_request.id)
        action = super(HrOvertimeRequestMass, self).action_schedule()
        if approval_required and self.approval_id:
            res = self.env.ref('viin_hr_overtime_approval.approval_request_view_form', False)
            action.update({
                'name': _('Overtime Approval Request'),
                'view_mode': 'form',
                'res_model': 'approval.request',
                'views': [(res and res.id or False, 'form')],
                'type': 'ir.actions.act_window',
                'res_id': self.approval_id.id
            })
        return action
