from odoo import models, fields


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    approval_id = fields.Many2one('approval.request', string='Approval Request', readonly=True)
