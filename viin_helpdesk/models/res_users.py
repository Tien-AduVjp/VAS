from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    helpdesk_team_ids = fields.Many2many('helpdesk.team', string='Helpdesk Teams')
