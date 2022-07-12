from odoo import models, fields


class ApprovalRequestType(models.Model):
    _inherit = 'approval.request.type'

    type = fields.Selection(selection_add=[('overtime', 'Overtime')], ondelete={'overtime': 'cascade'})
