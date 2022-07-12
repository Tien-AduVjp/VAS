from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TypeApprovalUserLine(models.Model):
    _name = 'type.approval.user.line'
    _inherit = 'abstract.approval.user.line'
    _description = "Type Approval User Line"

    request_type_id = fields.Many2one('approval.request.type', string='Request Type', required=True, ondelete='cascade')

    @api.constrains('user_id')
    def _check_user_id(self):
        for r in self:
            if not r.user_id.has_group('to_approvals.group_approval_officer'):
                raise UserError(_("Only users that belong to the group Approval Officer"
                                  " can be added as an approver to approve approval requests."
                                  " %s does not belong to that group.")
                                  % r.user_id.name)

    def _prepare_request_approval_user_line_vals(self):
        self.ensure_one()
        return {
            'sequence': self.sequence,
            'user_id': self.user_id.id,
            'required': self.required
            }
