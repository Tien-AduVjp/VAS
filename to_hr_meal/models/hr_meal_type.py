from odoo import models, fields


class HrMealType(models.Model):
    _name = 'hr.meal.type'
    _description = 'HR Meal Type'
    _inherit = ['mail.thread']

    name = fields.Char(string='Title', required=True, translate=True)
    alert_id = fields.Many2one('hr.meal.type.alert', string='Alert', required=True,
                               help='Alert message to be used when a meal order with this meal type is placed')

    scheduled_hour = fields.Float(string='Scheduled Hour', related='alert_id.scheduled_hour', store=True)

    price = fields.Float(string='Price', default=0.0, required=True)
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The meal type's title must be unique"),
    ]

