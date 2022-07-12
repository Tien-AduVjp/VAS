from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    state_group_id = fields.Many2one('res.state.group', string='State Group', related='state_id.state_group_id', store=True, ondelete='restrict')
