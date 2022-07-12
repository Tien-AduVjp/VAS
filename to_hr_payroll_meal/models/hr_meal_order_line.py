from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrMealOrderLine(models.Model):
    _inherit = 'hr.meal.order.line'
    
    employee_price = fields.Float(string='Employee Price', compute='_compute_employee_price', store=True,
                                  readonly=False, states={
                                      'confirmed': [('readonly', True)],
                                      'approved': [('readonly', True)],
                                      'refused': [('readonly', True)],
                                      'cancelled': [('readonly', True)]}
                                  )
    employee_amount = fields.Float(string='Employee Amount', compute='_compute_amount', store=True)
    company_amount = fields.Float(string="Company Amount", compute='_compute_amount', store=True)
    hr_payslip_id = fields.Many2one('hr.payslip', string='Pay Slip', readonly=True)

    @api.depends('employee_id', 'meal_order_id.company_id')
    def _compute_employee_price(self):
        for r in self:
            # TODO: contract should match the order date instead of current contract
            r.employee_price = r.employee_id.contract_id.pay_per_meal or r.meal_order_id.company_id.default_meal_emp_price
    
    @api.depends('employee_price', 'quantity', 'total_price')
    def _compute_amount(self):
        for r in self:
            employee_amount = r.employee_price * r.quantity
            r.employee_amount = employee_amount
            r.company_amount = r.total_price - employee_amount
            
    def unlink(self):
        for r in self:
            if r.hr_payslip_id:
                raise ValidationError(_("You must not delete a meal order line while it refers to a HR Payslip."
                                        " Please cancel the payslip %s first.") % r.hr_payslip_id.display_name)
        return super(HrMealOrderLine, self).unlink()
