from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrMealOrder(models.Model):
    _inherit = 'hr.meal.order'
        
    total_employee_pay = fields.Float('Employee Total Pay', compute='_compute_total_pay', store=True)
    total_company_pay = fields.Float('Company Total Pay', compute='_compute_total_pay', store=True)

    def _prepare_meal_order_line(self, employee):
        data = super(HrMealOrder, self)._prepare_meal_order_line(employee)
        # TODO: contract should match the order date instead of current contract
        data['employee_price'] = employee.sudo().contract_id.pay_per_meal or self.company_id.default_meal_emp_price or 0
        return data
    
    @api.depends('order_line_ids', 'order_line_ids.employee_amount', 'order_line_ids.company_amount')
    def _compute_total_pay(self):
        for order in self:
            total_employee_pay = 0.0
            total_company_pay = 0.0
            for line in order.order_line_ids:
                total_employee_pay += line.employee_amount
                total_company_pay += line.company_amount
            order.total_employee_pay = total_employee_pay
            order.total_company_pay = total_company_pay
    
    def action_refuse(self):
        for r in self:
            for line in r.order_line_ids.sudo():
                if line.hr_payslip_id:
                    raise ValidationError(_("You may not be able to refuse the order '%s' while it is referred by the payslips '%s'\n"
                                        "Please cancel the payslips first.")
                                      % (r.display_name, line.hr_payslip_id.display_name))
        super(HrMealOrder, self).action_refuse()
    
    def action_cancel(self):
        for r in self:
            hr_payslips = r.order_line_ids.sudo().mapped('hr_payslip_id')
            if hr_payslips:
                raise ValidationError(_("You must not cancel the order %s while it is referred by the following HR payslips: %s\n"
                                        "Please delete the payslips first.")
                                      % (r.name, ', '.join(hr_payslips.sudo().mapped('name'))))
        super(HrMealOrder, self).action_cancel()
            
