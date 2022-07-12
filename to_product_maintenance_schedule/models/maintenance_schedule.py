from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MaintenanceSchedule(models.Model):
    _name = 'maintenance.schedule'
    _description = 'Maintenance Schedule'

    part = fields.Char(string='Part', required=True)
    product_milestone_id = fields.Many2one('product.milestone', string='Milestone', required=True)
    maintenance_action_id = fields.Many2one('maintenance.action', string='Action', required=True)
    part_replacement = fields.Boolean(string='Part Replacement', related='maintenance_action_id.part_replacement', store=True, readonly=True)
    product_id = fields.Many2one('product.product', string='Replace Part')

    _sql_constraints = [
        ('maintenance_schedule_on_part_unique',
         'unique(part,product_milestone_id)',
         _("Maintenance Schedule must be unique!")),
    ]

    @api.constrains('product_id', 'part_replacement')
    def _check_product_id(self):
        for r in self:
            if r.part_replacement and not r.product_id:
                raise ValidationError(_("Please select replace part for replace maintenance actions."))

    def _get_display_name(self):
        return "%s - %s [%s]" % (self.part, self.maintenance_action_id.name, self.product_milestone_id.name)

    def name_get(self):
        return [(p.id, p._get_display_name()) for p in self]
