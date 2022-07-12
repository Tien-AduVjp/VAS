from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"
    
    zoom_api_key = fields.Char(string='Zoom Api Key', groups='to_zoom_calendar.group_admin')
    zoom_secret_key = fields.Char(string='Zoom Secret Key', groups='to_zoom_calendar.group_admin')