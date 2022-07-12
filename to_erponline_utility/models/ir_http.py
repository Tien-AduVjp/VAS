from odoo import models
from odoo.http import request
from odoo.tools import config


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(Http, self).session_info()

        user = request.env.user
        saaslimit_section = config.misc.get('saaslimits', {})
        is_trial = saaslimit_section.get('is_trial', False)
        trial_activated = saaslimit_section.get('trial_activated', False)
        stop_date = saaslimit_section.get('stop_date', False)
        activation_email = saaslimit_section.get('activation_email', False)
        trial_days = saaslimit_section.get('trial_days', False)
        if is_trial:
            if user.has_group('base.group_system'):
                activation_warning = 'admin'
            else:
                activation_warning = 'user'
            result.update({
                'activation_warning': activation_warning,
                'trial_activated': trial_activated,
                'stop_date': stop_date,
                'activation_email': activation_email,
                'trial_days': trial_days
            })

        return result
