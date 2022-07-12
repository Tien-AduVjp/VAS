from odoo import models, fields


class HrApprovalType(models.Model):
    _inherit = 'approval.request.type'

    type = fields.Selection(selection_add=[('timesheets', 'Timesheets')], ondelete={'timesheets': 'cascade'})
