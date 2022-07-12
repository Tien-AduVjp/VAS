from odoo import fields, models, _
from odoo.exceptions import ValidationError, UserError

STATUS = [
    ('draft', 'Draft'),
    ('confirm', 'To Approve'),
    ('validate', 'Approved'),
    ('done','Done'),
    ('refuse', 'Refused'),
    ('cancel', 'Cancelled')]


class AbstractApprovalRequestLine(models.AbstractModel):
    _name = 'abstract.approval.request.line'
    _description = 'Approval Request Line Abstract'

    approval_id = fields.Many2one('approval.request', string='Approval Request',
                                  help="The related approval request of this record.")
    currency_id = fields.Many2one('res.currency', string='Currency', related='approval_id.currency_id')
    amount = fields.Monetary(string='Amount')

    def _get_state_field(self):
        raise ValidationError(_("The state field has not been implemented for the model '%s' yet. Please define one") % self._name)

    def ensure_can_change_state(self):
        for r in self:
            if not r.approval_id:
                raise UserError(_("You can not change state of the record '%s' which is not referred by any Approval Request.") % r.display_name)

    def action_confirm(self):
        self.ensure_can_change_state()
        for r in self:
            if not r.approval_id.can_confirm:
                raise UserError(_("You don't have appropriate permission to confirm the '%s'") % r.display_name)
        self.write({
            self._get_state_field(): 'confirm',
            })

    def action_validate(self):
        self.ensure_can_change_state()
        for r in self:
            if not r.approval_id.can_validate and not self.env.context.get('bypass_check', False):
                raise UserError(_("You don't have appropriate permission to validate the '%s'") % r.display_name)
        self.write({
            self._get_state_field(): 'validate',
            })

    def action_refuse(self):
        self.ensure_can_change_state()
        for r in self:
            if not r.approval_id.can_refuse:
                raise UserError(_("You don't have appropriate permission to refuse the '%s'") % r.display_name)
        self.write({
            self._get_state_field(): 'refuse',
            })

    def action_cancel(self):
        self.ensure_can_change_state()
        self.write({
            self._get_state_field(): 'cancel',
            })

    def action_draft(self):
        self.ensure_can_change_state()
        self.write({
            self._get_state_field(): 'draft',
            })
