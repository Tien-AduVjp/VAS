from odoo import fields, models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    crm_team_id = fields.Many2one('crm.team', string='Sales Team', index=True)

    @api.model
    def create(self, vals):
        if vals.get('session_id'):
            # set crm_team based on the team specified on the config
            session = self.env['pos.session'].browse(vals['session_id'])
            if session.config_id.crm_team_id:
                vals['crm_team_id'] = session.config_id.crm_team_id.id
        return super(PosOrder, self).create(vals)
