from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class AbstractSalesTarget(models.AbstractModel):
    _name = 'abstract.sales.target'
    _inherit = 'mail.thread'
    _description = 'Team Sales Target'
    _order = 'start_date DESC, id'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Waiting Approved'),
        ('refused', 'Refused'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, index=True, readonly=True)

    start_date = fields.Date(string='Start Date', index=True, required=True, readonly=False, states={'confirmed': [('readonly', True)],
                                                                                                     'refused': [('readonly', True)],
                                                                                                     'approved': [('readonly', True)],
                                                                                                     'done': [('readonly', True)],
                                                                                                     'cancelled': [('readonly', True)]})
    end_date = fields.Date(string='End Date', index=True, required=True, readonly=False, states={'confirmed': [('readonly', True)],
                                                                                                 'refused': [('readonly', True)],
                                                                                                 'approved': [('readonly', True)],
                                                                                                 'done': [('readonly', True)],
                                                                                                 'cancelled': [('readonly', True)]})

    target = fields.Float(string='Target', readonly=False, states={'confirmed': [('readonly', True)],
                                                                   'refused': [('readonly', True)],
                                                                   'approved': [('readonly', True)],
                                                                   'done': [('readonly', True)],
                                                                   'cancelled': [('readonly', True)]}, required=True,
                          digits='Product Price',
                          help="The sales target amount for the duration between the Start Date and the End Date")

    _sql_constraints = [
        ('target_positive_check',
         'CHECK(target > 0)',
         "The target must be a positive value!"),

        ('start_date_end_date_check',
         'CHECK(end_date >= start_date)',
         "The End Date must not be earlier than the Start Date"),
    ]

    def _is_zero_target(self):
        self.ensure_one()
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if float_is_zero(self.target, precision_digits=prec):
            res = True
        else:
            res = False
        return res

    def get_target_sum(self, start_date, end_date):
        target = 0.0
        for r in self:
            latest_start = max(r.start_date, start_date)
            earliest_end = min(r.end_date, end_date)
            overlap_days = (earliest_end - latest_start).days + 1
            target += (r.target * overlap_days) / ((r.end_date - r.start_date).days + 1)
        return target

    def unlink(self):
        for item in self:
            if item.state != 'draft':
                raise UserError(_("You can only delete records whose state is draft."))
        return super(AbstractSalesTarget, self).unlink()

    def action_confirm(self):
        for r in self:
            if r.state != 'draft':
                raise UserError(_("You cannot confirm a sales target that is not in draft state."))
        self.write({'state':'confirmed'})

    def action_draft(self):
        for r in self:
            if r.state not in ('cancelled', 'refused', 'done'):
                raise UserError(_("You cannot set a sales target to draft when it is neither in Cancelled nor Refused nor Done state."))
        self.write({'state':'draft'})

    def action_refuse(self):
        for r in self:
            if r.state != 'confirmed':
                raise UserError(_("You cannot refuse a sales target that is not in Waiting Approved state."))
        self.write({'state':'refused'})

    def action_approve(self):
        for r in self:
            if r.state != 'confirmed':
                raise UserError(_("You cannot approve a sales target that is not in Waiting Approved state."))
        self.write({'state':'approved'})

    def action_done(self):
        for r in self:
            if r.state != 'approved':
                raise UserError(_("You cannot set done a sales target that is not in Approved state."))
        self.write({'state': 'done'})

    def action_cancel(self):
        for r in self:
            if r.state not in ('refused', 'confirmed', 'approved'):
                raise UserError(_("You cannot cancel a Sales Target when it is neither in Waiting Approved nor Refused nor Approved state."))
        self.write({'state':'cancelled'})

    def write(self, vals):
        # This to fix issue related constraint 'start_date_end_date_check' raising in case sql write start_date column before end_date column
        if 'start_date' in vals:
            vals['start_date'] = vals.pop('start_date')
        return super(AbstractSalesTarget, self).write(vals)
