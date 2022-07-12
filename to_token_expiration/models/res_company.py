from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class ResCompany(models.Model):
    _inherit = 'res.company'

    rotating_token_life = fields.Float(string='Default Token Lifetime', default=0.0,
                                               help="The life time (in days) of a rotating token. Leave it empty or zero"
                                               " if you want a forever life for rotating tokens")

    @api.constrains('rotating_token_life')
    def _check_rotating_token_life(self):
        for r in self:
            if float_compare(r.rotating_token_life, 0.0, precision_digits=2) == -1:
                raise ValidationError(_("Default Token Life must be greater than or equal to zero"))

