from odoo import fields, models


class HrAdvandageTemplate(models.Model):
    _inherit = 'hr.advantage.template'

    overtime_base_factor = fields.Boolean(string='Overtime Base Factor',
                                          help="If enabled, advantages of this template will be added into the contract's"
                                          " Overtime Base Amount for overtime calculation.")
