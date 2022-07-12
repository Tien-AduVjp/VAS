from odoo import fields, models, api
from odoo.tools import float_compare


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    loyalty_id = fields.Many2one('loyalty.program', string='Loyalty Program', help="The loyalty program"
                                 " that will be used for sales of this channel")

    loyalty_point_ids = fields.One2many('loyalty.point', 'team_id', string='Loyalty Points')
    loyalty_points_given = fields.Float(string='Loyalty Points Given', compute='_compute_loyalty_points',
                                        help="Total loyalty points that have been given to the customers from sales of this channel")
    loyalty_points_spent = fields.Float(string='Loyalty Points Spent', compute='_compute_loyalty_points',
                                        help="Total loyalty points that have been spent by customers in this channel")

    @api.depends('loyalty_point_ids.points', 'loyalty_point_ids.team_id')
    def _compute_loyalty_points(self):
        for r in self:
            r.loyalty_points_given = sum(r.loyalty_point_ids.filtered(lambda p: float_compare(p.points, 0.0, precision_rounding=0.001) == 1).mapped('points'))
            r.loyalty_points_spent = sum(r.loyalty_point_ids.filtered(lambda p: float_compare(p.points, 0.0, precision_rounding=0.001) == -1).mapped('points'))

    def find_loyalty_program(self):
        self.ensure_one()
        return self.loyalty_id or False
