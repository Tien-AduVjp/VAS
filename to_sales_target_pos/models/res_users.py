from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    st_pos_order_ids = fields.One2many('pos.order', 'user_id', string='Pos Orders',
                                       domain=[('state', 'in', ('paid', 'done', 'invoiced'))],
                                       help="PoS orders that are in the state of either Paid or Done or Invoiced")

