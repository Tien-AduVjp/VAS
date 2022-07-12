from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_helpdesk_rating = fields.Boolean(string='Use Rating on Helpdesk', implied_group='viin_helpdesk.group_helpdesk_rating')
    helpdesk_team_id = fields.Many2one('helpdesk.team', string='Default Helpdesk Team',
                                               related='company_id.default_helpdesk_team_id', readonly=False,
                                               help="The default helpdesk team that will be assigned to the "
                                               "helpdesk ticket of this company once none is given.")

    module_viin_helpdesk_severity = fields.Boolean(string='Helpdesk Ticket Severity')

