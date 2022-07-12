from odoo import models, fields


class MaintenanceAction(models.Model):
    _name = 'maintenance.action'
    _description = 'Maintenance Action'

    name = fields.Char('Action', required=True, translate=True)
    service_id = fields.Many2one('product.product', string='Service', domain=[('type', '=', 'service')], required=True)
    part_replacement = fields.Boolean(string='Part Replacement', help="If checked, the action requires part replacement")

    _sql_constraints = [
        ('maintenance_action_unique',
         'unique(name)',
         "Maintenance Action Name must be unique!"),
    ]
