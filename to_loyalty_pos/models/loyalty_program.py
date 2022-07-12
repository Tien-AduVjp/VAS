# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    pos_config_ids = fields.One2many('pos.config', 'loyalty_id', string='Points of Sale', help="The points of sale that apply this program")

    @api.constrains('currency_id', 'pos_config_ids')
    def _check_currency_vs_pos_config(self):
        for r in self:
            for pos_config_id in r.pos_config_ids:
                loyalty_currency_id = r.currency_id or pos_config_id.company_id.currency_id
                if loyalty_currency_id != pos_config_id.currency_id:
                    raise ValidationError(_("The loyalty program '%s' is currently referred by the PoS '%s' which has different currency."
                                            " You would need to modify the PoS for another program before you could change the currency of this"
                                            " program.") % (r.name, pos_config_id.name))

