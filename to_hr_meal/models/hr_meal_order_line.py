from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class HrMealOrderLine(models.Model):
    _name = 'hr.meal.order.line'
    _description = 'HR Meal Order Line'

    meal_order_id = fields.Many2one('hr.meal.order', string='Meal Order Ref.', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='meal_order_id.company_id', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
                                  readonly=False, states={'confirmed': [('readonly', True)],
                                                          'approved': [('readonly', True)],
                                                          'refused': [('readonly', True)],
                                                          'cancelled': [('readonly', True)]})
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_department', store=True,
                                    readonly=False, states={'confirmed': [('readonly', True)],
                                                            'approved': [('readonly', True)],
                                                            'refused': [('readonly', True)],
                                                            'cancelled': [('readonly', True)]})
    partner_ids = fields.Many2many('res.partner', 'hr_meal_order_line_partner_rel', 'hr_meal_order_line_id', 'partner_id',
                                   string='Clients', domain=[('is_company', '=', False)], help='The clients who enjoy the meal with this employee',
                                   readonly=False, states={'confirmed': [('readonly', True)],
                                                           'approved': [('readonly', True)],
                                                           'refused': [('readonly', True)],
                                                           'cancelled': [('readonly', True)]})
    meal_type_id = fields.Many2one('hr.meal.type', string='Meal Type', required=True, compute='_compute_meal_type', store=True,
                                   readonly=False, states={'confirmed': [('readonly', True)],
                                                           'approved': [('readonly', True)],
                                                           'refused': [('readonly', True)],
                                                           'cancelled': [('readonly', True)]})
    quantity = fields.Integer(string='Quantity', required=True, compute='_compute_quantity', store=True,
                              readonly=False, states={'confirmed': [('readonly', True)],
                                                      'approved': [('readonly', True)],
                                                      'refused': [('readonly', True)],
                                                      'cancelled': [('readonly', True)]})
    price = fields.Float(string='Price', required=True, default=0.0, compute='_compute_price', store=True,
                         readonly=False, states={'confirmed': [('readonly', False)],
                                                 'approved': [('readonly', False)],
                                                 'refused': [('readonly', False)],
                                                 'cancelled': [('readonly', False)]})
    total_price = fields.Float(string='Amount', compute='_compute_total_price', store=True)
    description = fields.Text(string='Description', readonly=False, states={'confirmed': [('readonly', False)],
                                                                            'approved': [('readonly', False)],
                                                                            'refused': [('readonly', False)],
                                                                            'cancelled': [('readonly', False)]})
    kitchen_id = fields.Many2one(related='meal_order_id.kitchen_id', string='Kitchen', store=True)
    meal_date = fields.Datetime(string='Meal Date', compute='_compute_meal_date', store=True, index=True)
    state = fields.Selection(related='meal_order_id.state', store=True)

    @api.depends('price', 'quantity')
    def _compute_total_price(self):
        for r in self:
            r.total_price = r.price * r.quantity

    @api.depends('meal_type_id')
    def _compute_price(self):
        for r in self:
            if r.meal_type_id:
                r.price = r.meal_type_id.price
            else:
                r.price = 0.0

    @api.depends('meal_order_id.scheduled_date', 'meal_order_id.scheduled_hour')
    def _compute_meal_date(self):
        for r in self:
            if r.meal_order_id.scheduled_date and r.meal_order_id.scheduled_hour:
                minutes = int(round(r.meal_order_id.scheduled_hour * 60))
                time_str = "%02d:%02d:00" % divmod(minutes, 60)
                datetime_str = "%s %s" % (fields.Date.to_string(r.meal_order_id.scheduled_date), time_str)
                r.meal_date = datetime_str
            else:
                r.meal_date = fields.Date.today()

    @api.constrains('employee_id', 'meal_date', 'state')
    def constrains_employee_id_and_meal_date(self):
        for r in self:
            if r.state == 'draft':
                continue
            overlap = self.search([
                ('id', '!=', r.id),
                ('employee_id', '=', r.employee_id.id),
                ('meal_date', '=', r.meal_date),
                ('state', 'in', ('confirmed', 'approved'))], limit=1)
            if overlap:
                raise ValidationError(_("You cannot register more than one meal for the same employee '%s' at the same time."
                                        " '%s' was registered by the order %s.")
                                      % (overlap.employee_id.name, overlap.employee_id.name, overlap.meal_order_id.name))

    @api.depends('meal_order_id.meal_type_id')
    def _compute_meal_type(self):
        for r in self:
            r.meal_type_id = r.meal_order_id.meal_type_id and r.meal_order_id.meal_type_id or False

    @api.depends('employee_id')
    def _compute_department(self):
        for r in self:
            r.department_id = r.employee_id and r.employee_id.department_id or False

    @api.depends('partner_ids')
    def _compute_quantity(self):
        for r in self:
            r.quantity = len(r.partner_ids) + 1

    def unlink(self):
        for r in self:
            if r.state != 'draft':
                raise UserError(_("You may not be able to delete the meal order line which is not in Draft state. You may need to set it to Draft the meal order first"))
        return super(HrMealOrderLine, self).unlink()

