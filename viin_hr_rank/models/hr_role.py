from odoo import models, fields, api


class HrRole(models.Model):
    _inherit = 'hr.role'

    rank_ids = fields.One2many('hr.rank', 'role_id', string='Ranks', readonly=True)
