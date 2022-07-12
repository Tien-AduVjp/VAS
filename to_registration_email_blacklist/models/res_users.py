from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.http import request


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def signup(self, values, token=None):
        if request.env['ir.config_parameter'].sudo().get_param('block_blacklisted_registration_emails', False):
            # if to_signup_email_verification module is not installed, 'email' key not in values
            email = (values.get('email', '') or values.get('login', '')).lower().rstrip()
            blacklist_rule = self.env['email.blacklist.rule'].is_blacklisted(email)
            if blacklist_rule:
                msg = _("Your registration email was blacklisted and blocked by our administrations."
                        " The violated rule was `%s` and the reason was '%s'.") % (
                      blacklist_rule.name, blacklist_rule.reason_id.name)
                if blacklist_rule.reason_id.solution:
                    msg = _("%s Here is a solution for you to consider:\n%s") % (msg, blacklist_rule.reason_id.solution)
    
                raise UserError(msg)

        return super(ResUsers, self).signup(values, token)
