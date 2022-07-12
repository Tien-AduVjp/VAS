from odoo import fields, models, api,_
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    shareholder_ids = fields.One2many('res.partner.shareholder',
                                      'partner_id',
                                       string='Shareholders')

    @api.constrains('shareholder_ids', 'is_company')
    def _check_shareholder_ids(self):
        for r in self:
            if not r.is_company and r.shareholder_ids:
                raise ValidationError(_("As an individual, '%s' cannot have shareholders. Only companies can have shareholders")
                                      % r.display_name)

    def write(self, vals):
        if 'is_company' in vals and not vals['is_company']:
            self.shareholder_ids.unlink()
        return super(ResPartner, self).write(vals)

    def _calculate_total_ownership_rate(self):
        self.ensure_one()
        return sum(self.shareholder_ids.mapped('ownership_rate'))
