from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression


class HrOvertimePlan(models.Model):
    _name = 'hr.overtime.plan'
    _inherit = ['hr.overtime.plan', 'abstract.approval.request.line']

    approval_id = fields.Many2one(domain="[('type','=','overtime'),('company_id','=',company_id)]")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'To Approve'),
        ('validate', 'Approved'),
        ('done', 'Done'),
        ('refuse', 'Refused'),
        ('cancel', 'Cancelled')
        ], compute='_compute_state', string='Status', store=True)
    approval_state_exception = fields.Boolean(string='Approval Status Exception', readonly=True,
                                     help="This field indicates the status of this plan is an exception of its approval request."
                                     " For example: when a plan of a requests' is cancelled/refused while others are not, the plan"
                                     " will be marked as `Approval Status Exception`.")

    def unlink(self):
        if not self._context.get('force_delete', False):
            for r in self:
                if r.approval_id and r.approval_id.state != 'draft':
                    raise UserError(_("You may not be able to delete the overtime plan '%s' manually while it is referred by the approval request"
                                      " '%s' that is not in Draft state. You should set the request to draft first.")
                                      % (r.display_name, r.approval_id.display_name))
        return super(HrOvertimePlan, self).unlink()

    @api.model
    def _get_state_field(self):
        return 'state'

    def _get_overlap_domain(self):
        self.ensure_one()
        domain = super(HrOvertimePlan, self)._get_overlap_domain()
        domain = expression.AND([
            domain,
            ['|', ('state', '=', False), ('state', 'in', ('confirm', 'validate', 'done'))]
            ])
        return domain

    def action_cancel(self):
        super(HrOvertimePlan, self).action_cancel()
        if not self._context.get('ignore_overtime_approval_state_exception', False):
            self.filtered(lambda r: not r.approval_state_exception).write({'approval_state_exception': True})

    def action_refuse(self):
        super(HrOvertimePlan, self).action_refuse()
        if not self._context.get('ignore_overtime_approval_state_exception', False):
            self.filtered(lambda r: not r.approval_state_exception).write({'approval_state_exception': True})

    @api.depends('approval_id.state', 'approval_state_exception')
    def _compute_state(self):
        for r in self:
            if not r.approval_id:
                r.state = False
            else:
                if not r.approval_state_exception:
                    r.state = r.approval_id.state
                else:
                    r.state = r._origin.state or r.state

    def _compute_read_only(self):
        super(HrOvertimePlan, self)._compute_read_only()
        for r in self.filtered(lambda rec: rec.state in ('confirm', 'validate', 'done', 'refuse', 'cancel')):
            r.readonly = True

    @api.constrains('state', 'employee_id', 'date_start', 'date_end')
    def _check_overlap(self):
        for r in self:
            if r.state == False or r.state in ('confirm', 'validate', 'done'):
                super(HrOvertimePlan, r)._check_overlap()
            else:
                continue

    @api.constrains('approval_id')
    def _check_approval_id(self):
        for r in self:
            if r.approval_id and r.approval_id.type != 'overtime':
                raise UserError(_("The approval request '%s' is not an overtime request.") % r.approval_id.display_name)
