from datetime import datetime, timedelta

from odoo import models
from odoo.addons.auth_signup.models.res_partner import random_token


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def signup_prepare(self, signup_type="signup", expiration=False):
        """ generate a new token for the partners with the given validity, if necessary
            :param expiration: the expiration datetime of the token (string, optional)
        """
        for partner in self:
            company = partner.company_id or self.env.company
            token_life = company.rotating_token_life
            if not expiration and token_life:
                expiration = datetime.now() + timedelta(days=token_life)
            super(ResPartner, partner).signup_prepare(signup_type, expiration)
        return True
