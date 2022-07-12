from odoo import models, fields, api, _
from odoo.tools import config
from odoo.exceptions import UserError

from . import tools


class ResUser(models.Model):
    _inherit = 'res.users'

    is_user_app_subscription = fields.Boolean(string='Is User App Subscription?',
                                              compute='_compute_is_user_app_subscription',
                                              default=lambda self: self._default_is_user_app_subscription())
    is_trial_subscripion = fields.Boolean(string='Is trial subscription', compute='_compute_is_trial_subscripion',
                                           default=lambda self: self._default_is_trial_subscripion())

    def _default_is_user_app_subscription(self):
        saas_subscription_type = tools.get_saas_subscription_type()
        return saas_subscription_type == 'user_app'

    def _compute_is_user_app_subscription(self):
        for r in self:
            r.is_user_app_subscription = self._default_is_user_app_subscription()

    def _default_is_trial_subscripion(self):
        return tools.get_subscription_is_trial()

    def _compute_is_trial_subscripion(self):
        for r in self:
            r.is_trial_subscripion = self._default_is_trial_subscripion()

    def _check_saas_config(self):
        section = config.misc.get("saaslimits", {})
        max_uaccounts = 0
        if section:
            if not 'max_uaccounts' in section.keys():
                raise UserError(_('max_uaccounts has not been defined in odoo config yet.'
                                        ' Please contact ERPOnline support team for fixing. Thank you!'))
            else:
                if section['max_uaccounts']:
                    max_uaccounts = section['max_uaccounts']
                    if not max_uaccounts.isdigit():
                        raise UserError(_('max_uaccounts is not a digit in the configuration.'
                                                ' Please contact ERPOnline support team for fixing. Thank you!'))
                    max_uaccounts = int(max_uaccounts)

        return max_uaccounts

    def _get_internal_users_domain(self):
        return [('share', '=', False), ('active', '=', True)]

    @api.model
    def _get_internal_users_count(self):
        users = self.search(self._get_internal_users_domain())
        return users and len(users) or 0

    @api.model_create_multi
    def create(self, vals_list):
        max_uaccounts = self._check_saas_config()
        new_users = super(ResUser, self).create(vals_list)
        if tools.get_saas_subscription_type() != 'plan':
            return new_users
        if max_uaccounts > 0:
            user_count = self._get_internal_users_count()
            if user_count > max_uaccounts:
                raise UserError(_('Could not add a new non-shared and active user!\n'
                                        'Your maximum non-shares and active users allowed is %s while this operation will'
                                        ' make total number to become %s.\n'
                                        'Please consider to upgrade your ERPOnline plan or purchase additional user accounts'
                                        ' (at https://www.erponline.vn).')
                                      % (max_uaccounts, user_count))
        return new_users

    def write(self, vals):
        max_uaccounts = self._check_saas_config()

        res = super(ResUser, self).write(vals)
        if tools.get_saas_subscription_type() != 'plan':
            return res
        if max_uaccounts > 0:
            user_count = self._get_internal_users_count()
            if user_count > max_uaccounts:
                raise UserError(_('Could neither add a new non-shared/active user nor change portal/inactive user(s)'
                                        ' into non-shared/active one(s)! Your maximum non-shares and active users allowed'
                                        ' is %s while this operation will make total number to become %s.\n'
                                        'Please consider to upgrade your ERPOnline plan or purchase additional user'
                                        ' accounts (at https://www.erponline.vn).')
                                      % (max_uaccounts, user_count))

        return res

