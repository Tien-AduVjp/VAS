from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    meal_ids = fields.One2many('hr.meal.order.line', 'employee_id', string='Meals',
                               domain=[('state', '=', 'approved')],
                               help='Approved Meal Order Lines')

    meals_count = fields.Integer(string='Meals Count', compute='_compute_meals_count')

    @api.depends('meal_ids')
    def _compute_meals_count(self):
        data = self.env['hr.meal.order.line'].sudo().read_group([('employee_id', 'in', self.ids), ('state', '=', 'approved')], ['employee_id'], ['employee_id'])
        mapped_data = dict([(dict_data['employee_id'][0], dict_data['employee_id_count']) for dict_data in data])
        for r in self:
            r.meals_count = mapped_data.get(r.id, 0)

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    order_meal = fields.Boolean(string='Order Meal', default=True, help="Marked if this employee eat at the company")