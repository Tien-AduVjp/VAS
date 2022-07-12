from odoo import fields, models, api, _


class PartnerEquityRange(models.Model):
    _name = 'res.partner.equity.range'
    _description = 'Partner Equity Range'

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The name of the equity range must be unique!"),
    ]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (Copy)") % self.name
        return super(PartnerEquityRange, self).copy(default=default)
