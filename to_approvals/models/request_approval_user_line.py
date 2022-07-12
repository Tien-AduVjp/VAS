from odoo import models, fields, api, _


class RequestApprovalUserLine(models.Model):
    _name = 'request.approval.user.line'
    _inherit = 'abstract.approval.user.line'
    _rec_name = 'approval_id'
    _description = "Request Approval User"

    approval_id = fields.Many2one('approval.request', string='Request', required=True, ondelete='cascade')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ], string='Status', required=True, default='draft', readonly=True, index=True, copy=False)
    date = fields.Datetime(string='Last Action Date', readonly=True, help="The latest date and time at which the"
                           " approver takes action of either refusing or approving the request.")

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, "[%s] %s to %s" % (r.approval_id.name, r.approval_id.title, r.user_id.name)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|',('title', '=ilike', name + '%'), ('name', operator, name), ('user_id.name','ilike', '%' + name + '%')]
        request = self.search(domain + args, limit=limit)
        return request.name_get()

    def _set_to_draft(self):
        self.write({
            'state': 'draft',
            'date': False
            })

    def _to_approve(self):
        self.write({'state': 'pending'})

    def _approve(self):
        self.write({
            'state': 'approved',
            'date': fields.Datetime.now()
            })
        for approval in self.approval_id:
            approval.message_post(body=_("%s approved the approval request `%s`.") % (self.env.user.name, approval.display_name))
            # Force fully approved if all approvers already approved
            if approval.state != 'validate' and all(line.state == 'approved' for line in approval.request_approval_user_line_ids):
                approval.write({
                    'state': 'validate'
                    })

    def _refuse(self):
        self.write({
            'state': 'refused',
            'date': fields.Datetime.now()
            })
        for approval in self.approval_id:
            approval.message_post(body=_("%s refused the approval request `%s`.") % (self.env.user.name, approval.display_name))

    def action_approve(self):
        self._approve()

    def action_refuse(self):
        self._refuse()
