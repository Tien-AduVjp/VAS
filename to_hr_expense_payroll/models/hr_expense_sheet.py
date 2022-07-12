from odoo import models, fields, api

class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    has_reimbursed_by_payslip_expense = fields.Boolean(compute='_compute_has_reimbursed_by_payslip_expense',
                                      help="Auto computed technical field to indicates if the sheet contains an expense that will be reimbursed in payslip.")
    is_paid = fields.Boolean(default=False, help="This field used to show/hide button Payment if this expense sheet has been fully paid, not included the expense is set to be paid by payslip")
    payslip_ids = fields.Many2many('hr.payslip', string='Payslips', compute='_compute_payslip_ids', store=True)
    payslips_count = fields.Integer(string='Payslips Count', compute='_compute_payslips_count')
    
    @api.depends('expense_line_ids.hr_payslip_id')
    def _compute_payslip_ids(self):
        for r in self:
            r.payslip_ids = [(6, 0, r.expense_line_ids.hr_payslip_id.ids)]
    
    def _compute_payslips_count(self):
        for r in self:
            r.payslips_count = len(r.payslip_ids)

    @api.depends('expense_line_ids.reimbursed_in_payslip', 'state')
    def _compute_has_reimbursed_by_payslip_expense(self):
        for r in self:
            r.has_reimbursed_by_payslip_expense = False
            if r.state in ('post', 'done') and r.expense_line_ids.filtered(lambda r: r.reimbursed_in_payslip):
                r.has_reimbursed_by_payslip_expense = True

    def set_to_paid(self):
        expense_line_ids = self.expense_line_ids.filtered(lambda r:r.reimbursed_in_payslip and r.state != 'done')
        if not expense_line_ids:
            super(HrExpenseSheet, self).set_to_paid()
    
    def approve_expense_sheets(self):
        super(HrExpenseSheet, self).approve_expense_sheets()
        for r in self:
            if not r.expense_line_ids.filtered(lambda x: not x.reimbursed_in_payslip):
                r.is_paid = True
    
    def _get_amount(self):
        amount_reimbursed_in_payslip = sum(self.expense_line_ids.filtered(lambda x: x.reimbursed_in_payslip).mapped('total_amount'))  
        amount_residual = abs(sum(self.account_move_id.line_ids.filtered(lambda l: l.account_id.internal_type == 'payable').mapped('amount_residual')))
        return max(amount_residual - amount_reimbursed_in_payslip, 0)
    
    def action_view_payslips(self):
        action = self.env.ref('to_hr_payroll.action_view_hr_payslip_form')
        result = action.read()[0]

        # choose the view_mode accordingly
        if self.payslips_count != 1:
            result['domain'] = "[('id', 'in', %s)]" % str(self.payslip_ids.ids)
        elif self.payslips_count == 1:
            res = self.env.ref('to_hr_payroll.view_hr_payslip_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.payslip_ids.id
        return result
