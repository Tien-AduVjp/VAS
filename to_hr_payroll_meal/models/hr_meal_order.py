from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrMealOrder(models.Model):
    _inherit = 'hr.meal.order'

    total_employee_pay = fields.Monetary('Employee Total Pay', compute='_compute_total_pay', store=True)
    total_company_pay = fields.Monetary('Company Total Pay', compute='_compute_total_pay', store=True)

    def _prepare_meal_order_line(self, employee):
        data = super(HrMealOrder, self)._prepare_meal_order_line(employee)
        contracts = employee.sudo()._get_contracts(self.scheduled_date, self.scheduled_date, states=['open', 'close'])
        # if the actual meal price is less than the contracted price, take the actual meal price.
        # otherwise, the employee just has to pay at the contracted price
        data['employee_price'] = min(self.meal_type_id.price, contracts[:1].pay_per_meal or self.company_id.default_meal_emp_price)
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

    def action_confirm(self):
        res = super(HrMealOrder, self).action_confirm()
        for r in self:
            if r.order_line_ids:
                r.order_line_ids._check_related_payslips()
        return res

    def write(self, vals):
        res = super(HrMealOrder, self).write(vals)
        if vals.get('scheduled_date', False):
            self.order_line_ids._check_related_payslips()
        return res
