from odoo import api, fields, models


class MrpEcoRoutingChange(models.Model):
    _name = 'mrp.eco.routing.change'
    _description = 'Eco Routing changes'

    eco_id = fields.Many2one('mrp.eco', ondelete='cascade', string='Engineering Change', required=True)
    change_type = fields.Selection([
        ('add', 'Add'),
        ('remove', 'Remove'),
        ('update', 'Update')], string='Type', required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center')
    old_time_cycle_manual = fields.Float(string='Previous Manual Duration', default=0)
    new_time_cycle_manual = fields.Float(string='New manual duration', default=0)
    upd_time_cycle_manual = fields.Float(string='Manual Duration Change', compute='_compute_upd_time_cycle_manual', store=True)

    @api.depends('new_time_cycle_manual', 'old_time_cycle_manual')
    def _compute_upd_time_cycle_manual(self):
        for r in self:
            r.upd_time_cycle_manual = r.new_time_cycle_manual - r.old_time_cycle_manual
