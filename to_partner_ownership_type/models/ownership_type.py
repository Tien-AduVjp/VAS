from odoo import fields, models, api, _


class PartnerBusinessType(models.Model):
    _name = 'res.partner.ownership.type'
    _description = 'Partner Business Type'

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The name of the equity range must be unique!"),
    ]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _('%s (Copy)') % self.name
        return super(PartnerBusinessType, self).copy(default=default)
