from odoo import models, fields, api


class SocialNotice(models.Model):
    _inherit = 'social.notice'

    linkedin_notification_id = fields.Char(string='Linkedin Notification Id')

    _sql_constraints = [
        ('linkedin_notification_id_unique',
         'UNIQUE(linkedin_notification_id)',
         "The Linkedin Notification Id must be unique!"),
    ]

    def _get_post_link(self):
        self.ensure_one()
        if self.page_id.social_provider == 'linkedin':
            # Haven't figured out how to get the url of the linkedin post yet
            return ''
        return super(SocialNotice, self)._get_post_link()
