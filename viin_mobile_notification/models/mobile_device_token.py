from odoo import models, fields


class MobileDeviceToken(models.Model):
    _name = 'mobile.device.token'
    _description = "Device Token"

    token = fields.Char(string='Device token', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    consecutive_error = fields.Integer(string='Number of consecutive error', readonly=True, default=0)
    platform = fields.Char(string='Platform', readonly=True)
    package_name = fields.Char(string='Version platform', readonly=True)
