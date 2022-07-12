import datetime
import logging

from odoo import models, fields, api
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class RotatingTokenMixing(models.AbstractModel):
    _name = 'rotating.token.mixin'
    _description = "Rotating Token Mixin"

    rotating_token_id = fields.Many2one('rotating.token', string='Rotating Token', readonly=True,
                                        help="Technical field to store a rotating token record for access token computation")
    access_token = fields.Char('Security Token', compute='_compute_access_token', store=True, copy=False, compute_sudo=True, index=True)

    @api.depends('rotating_token_id', 'rotating_token_id.name')
    def _compute_access_token(self):
        for r in self:
            r.access_token = r.rotating_token_id.name if r.rotating_token_id else False

    def _ensure_rotating_token(self):
        """ Ensure the token is available and valid """
        if not self.access_token or (self.rotating_token_id and self.rotating_token_id.is_expired()):
            self._generate_token()
        return self.access_token

    def _get_token_lifetime(self):
        """
        Get token lifetime in days
        
        :return: positive float or False
        """
        rotating_token_life = False
        if hasattr(self, 'company_id'):
            if float_compare(self.company_id.rotating_token_life, 0.0, precision_digits=2) == 1:
                rotating_token_life = self.company_id.rotating_token_life
        else:
            _logger.warning("The model %s should implement company_id field to have rotating token feature.")
        # return life time in days or False
        return rotating_token_life

    def _get_expiration_date(self):
        rotating_token_life = self._get_token_lifetime()
        if rotating_token_life:
            return fields.Datetime.now() + datetime.timedelta(days=rotating_token_life)
        else:
            return False

    def _prepare_rotating_token_data(self):
        return {
            'model': self._name,
            'res_id': self.id,
            'expiration': self._get_expiration_date()
            }

    def _generate_token(self):
        old_tokens = self.mapped('rotating_token_id')
        vals_list = [r._prepare_rotating_token_data() for r in self]
        # users may not have create access right, hence we implement sudo() here
        new_tokens = self.env['rotating.token'].sudo().create(vals_list)
        # TODO: the code below may not be needed as the create method already did the same task
        # please inspect this case carefully before remove the code
        old_tokens = old_tokens.exists()
        if old_tokens:
            old_tokens.unlink()
        return new_tokens

    @api.model_create_multi
    def create(self, vals_list):
        records = super(RotatingTokenMixing, self).create(vals_list)
        records._generate_token()
        return records

    def rotate_token(self):
        self._generate_token()

    def action_rotate_token(self):
        self.rotate_token()
