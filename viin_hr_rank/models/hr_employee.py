from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # begin override
    rank_id = fields.Many2one(tracking=True)
    next_rank_id = fields.Many2one(tracking=True)
    # end override

