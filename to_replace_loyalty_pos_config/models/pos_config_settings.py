from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    module_to_loyalty_pos = fields.Boolean(string='Loyalty program', help="""Install the module that allows to use loyalty program""")
