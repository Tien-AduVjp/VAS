from odoo import models, fields


class ApprovalRequestType(models.Model):
    _inherit = 'approval.request.type'

    type = fields.Selection(selection_add=[('stock_allocation', 'Stock Allocation')], ondelete={'stock_allocation': 'cascade'})
