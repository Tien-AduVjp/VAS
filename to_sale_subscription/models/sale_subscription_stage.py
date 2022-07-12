from odoo import fields, models


class SaleSubscriptionStage(models.Model):
    _name = 'sale.subscription.stage'
    _description = 'Subscription Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    fold = fields.Boolean(string='Folded in Kanban',
                          help="If checked, this stage is folded in the kanban view.")
    rating_template_id = fields.Many2one('mail.template', string='Rating Email Template', 
                                         domain=[('model', '=', 'sale.subscription')],
                                         help="If set and if the subscription's Customer(s) Ratings configuration is checked, "
                                         "then an email will be sent to the customer when the subscription reaches this step.")
    in_progress = fields.Boolean(string='In Progress', default=True)
