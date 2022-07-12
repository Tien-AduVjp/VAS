from odoo import models, fields


class DriverLicenseClass(models.Model):
    _name = 'driver.license.class'
    _description = 'License Class'

    name = fields.Char(string='Class', required=True)
    description = fields.Text(string='Description', translate=True)
    licence_ids = fields.One2many('fleet.driver.license', 'class_id', string='Licenses')
