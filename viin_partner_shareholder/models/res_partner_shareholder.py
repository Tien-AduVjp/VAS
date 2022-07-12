from odoo import fields,models,api,_
from odoo.exceptions import ValidationError


class Shareholder(models.Model):
    _name = 'res.partner.shareholder'
    _description = 'Partner Shareholder'

    partner_id = fields.Many2one('res.partner', string='Partner',
                                  required=True, domain="[('is_company','=',True)]",
                                  ondelete='cascade') #Company
    shareholder_id = fields.Many2one('res.partner', string='Shareholder',
                                      required=True, ondelete='cascade') #Person
    # it was `owned_percentage` before version 14
    ownership_rate = fields.Float(string='Ownership Rate', required=True,
                                  help="The ownership rate (in percentage) of the shareholder in the company")
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('check_ownership_rate', 'CHECK(ownership_rate > 0 and ownership_rate <= 100)',
         "The ownership rate of a shareholder should be greater than 0 and not greater than 100.")
        ]

    @api.constrains('ownership_rate','partner_id')
    def _check_ownership_rate_partner_id(self):
        for partner in self.partner_id:
            if partner.is_company:
                if partner._calculate_total_ownership_rate() > 100:
                    raise ValidationError(_("The total shareholder ownership rate of the partner `%s` must not be greater than 100 percentage. Please choose another number.")
                          % partner.display_name)
            else:
                raise ValidationError(_("As an individual, the partner '%s' cannot have shareholders. Only company can have shareholders.")
                                      % partner.display_name)
