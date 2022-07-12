from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    partner_type = fields.Selection(selection_add=[('employee', 'Employee')], ondelete={'employee': 'set default'})
    employee_id = fields.Many2one('hr.employee', string='Employee', check_company=True,
                                  readonly=True, states={'draft': [('readonly', False)]})

    @api.depends('partner_type', 'employee_id')
    def _compute_partner_id(self):
        super(AccountPayment, self)._compute_partner_id()
        for r in self.filtered(lambda p: p.partner_type == 'employee' and p.employee_id):
            r.partner_id = r.employee_id.sudo().address_home_id

    @api.depends('employee_id', 'payment_type')
    def _compute_destination_account_id(self):
        super(AccountPayment, self)._compute_destination_account_id()
        for r in self.filtered(lambda p: p.partner_type == 'employee' and p.employee_id):
            r.destination_account_id = r.employee_id._get_advance_account()

    def _prepare_payment_display_name(self):
        res = super(AccountPayment, self)._prepare_payment_display_name()
        res.update({
            'outbound-employee': _('Employee Reimbursement'),
            'inbound-employee': _('Employee Payment'),
        })
        return res
