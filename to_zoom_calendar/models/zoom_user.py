from odoo import models, api, fields, registry, _
from odoo.exceptions import AccessError, ValidationError


class ZoomUser(models.Model):
    _name = "zoom.user"
    _description = "Zoom User"

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    zoom_action = fields.Selection([('create', 'Create'),
                                    ('autoCreate', 'Auto Create'),
                                    ('custCreate', 'Cust Create'),
                                    ('ssoCreate', 'SSO Create')], string='Action', required=True, default='create',
                                   help='''Specify how to create the new user: \n
                                    1. "Create" - User will get an email sent from Zoom. There is a confirmation link in this email. User will then need to click this link to activate their account to the Zoom service. The user can set or change their password in Zoom.
                                    2. "Auto Create" - This action is provided for enterprise customer who has a managed domain. This feature is disabled by default because of the security risk involved in creating a user who does not belong to your domain without notifying the user.
                                    3. "Cust Create" - This action is provided for API partner only. User created in this way has no password and is not able to log into the Zoom web site or client.
                                    4. "SSO Create" - This action is provided for enabled “Pre-provisioning SSO User” option. User created in this way has no password. If it is not a basic user, will generate a Personal Vanity URL using user name (no domain) of the provisioning email. If user name or pmi is invalid or occupied, will use random number/random personal vanity URL.''')

    zoom_user_type = fields.Selection([('1', 'Basic'),
                                       ('2', 'Licensed'),
                                       ('3', 'On-prem')], string='User Type', required=True, default='1')
    zoom_email = fields.Char('User Email Address', required=True)
    zoom_first_name = fields.Char("User's First Name", required=True)
    zoom_last_name = fields.Char("User's Last Name", required=True)
    zoom_password_name = fields.Char('User Password', help='''The password has to have a minimum of 8 characters and maximum of 32 characters. By default (basic requirement), password must have at least one letter (a, b, c…), at least one number (1, 2, 3…) and include both uppercase and lowercase letters. It should not contain only one identical character repeatedly (‘11111111’ or ‘aaaaaaaa’) and it cannot contain consecutive characters (‘12345678’ or ‘abcdefgh’).''')

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "%s %s (%s)" % (record.zoom_first_name, record.zoom_last_name, record.zoom_email)))
        return result

    def _prepare_zoom_user_values_to_create(self, vals):
        """Prepare the dict of values to create the Zoom User"""
        data = {
            "action": vals.get('zoom_action'),
            "user_info": {
                "email": vals.get('zoom_email'),
                "type": vals.get('zoom_user_type'),
                "first_name": vals.get('zoom_first_name'),
                "last_name": vals.get('zoom_last_name')
            }
        }
        return data

    def _prepare_zoom_user_values_to_update(self):
        """Prepare the dict of values to update the Zoom User"""
        data = {
            "type": self.zoom_user_type,
            "first_name": self.zoom_first_name,
            "last_name": self.zoom_last_name
        }
        return data

    @api.model
    def create(self, vals):
        user_level_app = vals.get('user_level_app', False)
        if user_level_app:
            del vals['user_level_app']

        if not user_level_app:
            req = self.env['zoom.apiv2'].create_user(self._prepare_zoom_user_values_to_create(vals))
            if req.status_code != 201:
                result = req.json()
                raise ValidationError('Zoom: %s' % result.get('message', False))
        return super(ZoomUser, self).create(vals)

    def write(self, vals):
        req = self.env['zoom.apiv2'].update_user(self.zoom_email, self._prepare_zoom_user_values_to_update())
        if req.status_code != 204:
            result = req.json()
            raise ValidationError('Zoom: %s' % result.get('message', False))

        return super(ZoomUser, self).write(vals)

    def unlink(self):
        if self._context.get('reset_zoom_user'):
            return super(ZoomUser, self).unlink()

        req = self.env['zoom.apiv2'].delete_user(self.zoom_email)
        if req.status_code != 204:
            result = req.json()
            raise ValidationError('Zoom: %s' % result.get('message', False))

        return super(ZoomUser, self).unlink()
