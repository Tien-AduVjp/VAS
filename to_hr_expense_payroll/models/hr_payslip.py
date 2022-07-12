from odoo import fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    hr_expense_ids = fields.One2many('hr.expense', 'hr_payslip_id', string='HR Expenses', readonly=True)

    def _prepare_hr_expense_domain(self):
        return [
            ('employee_id', 'in', self.employee_id.ids),
            ('state', '=', 'approved'),
            ('payment_mode', '=', 'own_account'),
            ('reimbursed_in_payslip', '=', True),
            ('company_id', 'in', self.company_id.ids),
            '|', ('hr_payslip_id', '=', False), ('hr_payslip_id', 'in', self.ids)
        ]

    def _link_hr_expenses(self):
        all_hr_expenses = self.env['hr.expense'].sudo().search(self._prepare_hr_expense_domain())
        for r in self:
            existing_expenses = r._origin.hr_expense_ids if r._origin else r.r.hr_expense_ids
            # find expenses to add and expense to remove
            hr_expenses = all_hr_expenses.filtered(lambda exp: exp.employee_id == r.employee_id and exp.date <= r.date_to)
            to_remove_expenses = existing_expenses.filtered(lambda exp: exp.id not in hr_expenses.ids)
            new_hr_expenses = hr_expenses.filtered(lambda exp: exp.id not in existing_expenses.ids)
            cmd = [(3, expense.id) for expense in to_remove_expenses] + [(4, expense.id) for expense in new_hr_expenses]
            r.hr_expense_ids = cmd

    def compute_sheet(self):
        self._link_hr_expenses()
        return super(HrPayslip, self).compute_sheet()

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        # payroll officers may not have write access right to modify hr.expense and
        # hr.expense.sheet, sudo() is implemented here to bypass access rights check
        hr_expenses = self.hr_expense_ids.sudo()
        hr_expenses.write({'state':'done'})
        for sheet in hr_expenses.sheet_id:
            if all(expense.state == 'done' for expense in sheet.expense_line_ids) and sheet.state == 'post':
                sheet.set_to_paid()
                # the hr.expense's state is recompute after the sheet is set to paid
                # we need to override them again
                sheet.expense_line_ids.write({'state':'done'})
        return res

    def action_payslip_cancel(self):
        for r in self:
            if r.hr_expense_ids:
                # payroll officers may not have write access right to modify hr.expense and
                # hr.expense.sheet, sudo() is implemented here to bypass access rights check
                expenses = r.hr_expense_ids.sudo()
                for sheet in expenses.sheet_id:
                    if sheet.state == 'done' and sheet.move_ids:
                        sheet.state = 'post'
                    else:
                        sheet.state = 'approve'
                expenses.write({
                    'state': 'approved',
                    'hr_payslip_id': False,
                    })
        return super(HrPayslip, self).action_payslip_cancel()
