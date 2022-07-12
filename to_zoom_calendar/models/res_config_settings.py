from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    module_to_zoom_calendar = fields.Boolean("Zoom Integration")
    zoom_api_key = fields.Char(related='company_id.zoom_api_key', readonly=False, string='Zoom Api Key', groups='to_zoom_calendar.group_admin')
    zoom_secret_key = fields.Char(related='company_id.zoom_secret_key', readonly=False, string='Zoom Secret Key', groups='to_zoom_calendar.group_admin')
    
    @api.constrains('zoom_api_key', 'zoom_secret_key')
    def _constrains_zoom_api(self):
        for r in self:
            allusers = self.env['zoom.user'].search([]).with_context(reset_zoom_user=True)
            if allusers:
                allusers.unlink()
            if r.zoom_api_key and r.zoom_secret_key:
                zoom_apiv2 = self.env['zoom.apiv2']
                res = zoom_apiv2.get_user('me')
                result = res.json()
                if res.status_code == 200:
                    ''' Use `user_level_app` keyword to create a Zoom user by default in Odoo.'''
                    self.env['zoom.user'].create({
                        'zoom_first_name': result.get('first_name'),
                        'zoom_last_name': result.get('last_name'),
                        'zoom_email': result.get('email'),
                        'zoom_user_type': str(result.get('type')),
                        'user_level_app': True,
                        })
                else:
                    raise ValidationError('Zoom: %s' % result.get('message'))

