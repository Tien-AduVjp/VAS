from odoo import models, fields


class HrMealTypeAlert(models.Model):
    _name = 'hr.meal.type.alert'
    _description = 'Meal Type Alert'

    name = fields.Char(string='Title', required=True, translate=True)
    scheduled_hour = fields.Float(string='Scheduled Hour', required=True)
    message = fields.Text(string='Message', help="Alert message to be used when a meal order is placed", required=True, translate=True)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The meal type alert's title must be unique"),

        ('scheduled_hour_check_positive',
         'CHECK(scheduled_hour >= 0)',
         "The Scheduled Hour must be equal to or greater than zero!"),

        ('scheduled_hour_check_less_than_24',
         'CHECK(scheduled_hour < 24)',
         "The Scheduled Hour must be less than than 24!"),
    ]
