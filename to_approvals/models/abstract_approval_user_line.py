from odoo import models, fields

class AbstractApprovalUserLine(models.AbstractModel):
    _name = 'abstract.approval.user.line'
    _order = 'sequence ASC, id ASC'
    _description = "Approval User Abstract"

    sequence = fields.Integer(string='Sequence', default=10)
    user_id = fields.Many2one('res.users', string='Approver', required=True,
                              domain=lambda self: [('groups_id', 'in', [self.env.ref('to_approvals.group_approval_officer').id])],
                              help="Only users that belong to the group Approval Officer can be added here.")
    required = fields.Boolean(string='Required', default=False,
                              help="If enabled, the related approval requests require this user to approve.")
