from odoo import api, SUPERUSER_ID


def migrate(cr, registry):
    """This method will change value of key mobile.notify_type from nosy to noisy"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    mobile_notify_type = env['ir.config_parameter'].search([('key', '=', 'mobile.notify_type')])
    if mobile_notify_type.value == 'nosy':
        mobile_notify_type.value = 'noisy'
