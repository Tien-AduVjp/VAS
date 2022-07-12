from odoo import models, fields


class HrApprovalType(models.Model):
    _inherit = 'approval.request.type'

    type = fields.Selection(selection_add=[('maintenance_type', 'Maintenance')], ondelete={'maintenance_type': 'cascade'})
