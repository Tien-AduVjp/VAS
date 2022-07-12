from odoo import models, fields, api


class ConfigSection(models.Model):
    _name = 'config.section'
    _inherit = 'mail.thread'
    _description = "Configuration Section"

    name = fields.Char(string='Name', required=True, tracking=True)
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The Name of config section must be unique!"),
        ('name_description_check',
         'CHECK(name != description)',
         "The Name of the config section should not be the description"),
    ]

    @api.model
    def create_if_not_exist(self, vals):
        if 'name' in vals:
            existing = self.search([('name', '=', vals['name'])], limit=1)
            if existing:
                return existing
        return self.create(vals)

