from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    pos_config_ids = fields.One2many('pos.config', 'crm_team_id', string="Point of Sales")

    st_pos_order_ids = fields.One2many('pos.order', 'crm_team_id', string='PoS Orders',
                                       domain=[('state', 'in', ('paid', 'done', 'invoiced'))],
                                       help="PoS orders that are in the state of either Paid or Done or Invoiced")
