from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    nod_return_product = fields.Integer(string='Days to Return Products', default=0,
                                        help='The max number of days for returning sold product')

