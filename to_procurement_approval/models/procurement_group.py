from odoo import models, fields


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    procurement_request_line_ids = fields.One2many('procurement.request.line', 'procurement_group_id', string='Procurement Request Lines')
    approval_request_id = fields.Many2one('approval.request', string='Procurement Request')
