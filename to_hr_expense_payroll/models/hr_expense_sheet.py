from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    has_reimbursed_by_payslip_expense = fields.Boolean(compute='_compute_has_reimbursed_by_payslip_expense', string='Has Reimbursed',
                                      help="Auto computed technical field to indicates if the sheet contains an expense that will be reimbursed in payslip.")
    # This field is moved to module to_hr_expense, remove in v15
    is_paid = fields.Boolean(string='Is Paid')
    payslip_ids = fields.Many2many('hr.payslip', string='Payslips', compute='_compute_payslip_ids', store=True)
    payslips_count = fields.Integer(string='Payslips Count', compute='_compute_payslips_count')

    @api.depends('expense_line_ids.hr_payslip_id')
    def _compute_payslip_ids(self):
        for r in self:
            r.payslip_ids = [(6, 0, r.expense_line_ids.hr_payslip_id.ids)]

    @api.depends('payslip_ids')
    def _compute_payslips_count(self):
        for r in self:
            r.payslips_count = len(r.payslip_ids)

    @api.depends('expense_line_ids.reimbursed_in_payslip', 'state')
    def _compute_has_reimbursed_by_payslip_expense(self):
        for r in self:
            r.has_reimbursed_by_payslip_expense = False
            if r.state in ('post', 'done') and r.expense_line_ids.filtered(lambda r: r.reimbursed_in_payslip):
                r.has_reimbursed_by_payslip_expense = True

    @api.depends('expense_line_ids.reimbursed_in_payslip')
    def _compute_is_paid(self):
        res = super(HrExpenseSheet, self)._compute_is_paid()
        for r in self:
            r.is_paid = any(r.expense_line_ids.mapped('reimbursed_in_payslip'))
        return res

    def set_to_paid(self):
        expense_line_ids = self.expense_line_ids.filtered(lambda r:r.reimbursed_in_payslip and r.state != 'done')
        if not expense_line_ids:
            super(HrExpenseSheet, self).set_to_paid()

    # TODO: This method is deprecated, remove in v15
    def _get_amount(self):
        amount_reimbursed_in_payslip = sum(self.expense_line_ids.filtered(lambda x: x.reimbursed_in_payslip).mapped('total_amount'))
        payable_lines = self.move_ids.line_ids.filtered(lambda l: l.account_id.internal_type == 'payable')
        amount_residual = abs(sum(payable_lines.mapped('amount_residual')))
        return max(amount_residual - amount_reimbursed_in_payslip, 0)

    def action_view_payslips(self):
        result = self.env['ir.actions.act_window']._for_xml_id('to_hr_payroll.action_view_hr_payslip_form')

        # choose the view_mode accordingly
        if self.payslips_count != 1:
            result['domain'] = "[('id', 'in', %s)]" % str(self.payslip_ids.ids)
        elif self.payslips_count == 1:
            res = self.env.ref('to_hr_payroll.view_hr_payslip_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.payslip_ids.id
        return result

    def action_submit_sheet(self):
        for r in self:
            if len(set(r.expense_line_ids.mapped('reimbursed_in_payslip'))) != 1:
                raise ValidationError(_("Expense Sheet cannot include both Reimbursed in Payslip and Normally"))
        return super(HrExpenseSheet, self).action_submit_sheet()

    def action_sheet_move_create(self):
        res = super(HrExpenseSheet, self).action_sheet_move_create()
        sheets_done = self.sudo().filtered(lambda sheet: all(exp_line.hr_payslip_id.state == 'done' for exp_line in sheet.expense_line_ids))
        sheets_done.expense_line_ids.write({'state': 'done'})
        sheets_done.set_to_paid()
