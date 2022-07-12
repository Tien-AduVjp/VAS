from dateutil.relativedelta import relativedelta
from distutils.version import StrictVersion

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OdooVersion(models.Model):
    _name = 'odoo.version'
    _inherit = 'mail.thread'
    _order = 'end_of_life desc, release_date desc, name desc, id'
    _description = 'Odoo Version'

    name = fields.Char(string='Version', required=True, tracking=True, help="Version String, e.g. 8.0, 9.0, 10.0, etc")
    release_date = fields.Date(string='Release Date', required=True, tracking=True)
    end_of_functional_support = fields.Date(string='End of Functional Support', tracking=True,
                                            compute='_compute_end_of_functional_support', store=True, readonly=False,
                                            help="The date on which functional support will end. However, technical maintenance"
                                            " and bug fixing still the end of life of the version")
    end_of_life = fields.Date(string='End of Life', tracking=True,
                              compute='_compute_end_of_life', store=True, readonly=False,
                              help="No more support and maintenance, including bug fixes, would be made upon this date and later on."
                              " Users must have their Odoo instances upgraded before this date.")
    description = fields.Text(string='Description', translate=True)
    recommended = fields.Boolean(string='Recommended', default=True)
    config_ids = fields.One2many('odoo.version.config', 'odoo_version_id', string='Standard Config. Directives')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The version string (Name) must be unique!"),
    ]

    @api.constrains('name')
    def _validate_version_string(self):
        for r in self:
            try:
                StrictVersion(r.name)
            except ValueError:
                raise ValidationError(_("Invalid version number %s. The version should be in the form of either 'x.y' or 'x.y.z'"
                                        " where the x, y, z must be digits.") % r.name)

    @api.depends('release_date')
    def _compute_end_of_functional_support(self):
        for r in self:
            r.end_of_functional_support = r.release_date + relativedelta(years=3) if r.release_date else False

    @api.depends('release_date', 'end_of_functional_support')
    def _compute_end_of_life(self):
        for r in self:
            if r.end_of_functional_support:
                r.end_of_life = r.end_of_functional_support + relativedelta(years=2)
            else:
                if r.release_date:
                    r.end_of_life = r.release_date + relativedelta(years=5)
                else:
                    r.end_of_life = False

    @api.model
    def create(self, vals):
        res = super(OdooVersion, self).create(vals)
        if res.recommended:
            self.search([('id', '!=', res.id)]).write({'recommended':False})
        return res

    def write(self, vals):
        res = super(OdooVersion, self).write(vals)
        if 'recommended' in vals and vals['recommended'] == True and len(self) >= 1:
            self.search([('id', '!=', self[0].id)]).write({'recommended':False})
        return res

    def configs_to_text(self):
        self.ensure_one()
        return self.config_ids.to_text()

