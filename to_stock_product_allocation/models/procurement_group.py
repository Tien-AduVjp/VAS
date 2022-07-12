from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    stock_allocation_request_line_ids = fields.One2many('stock.allocation.request.line', 'procurement_group_id', string='Stock Allocation Request Lines')
    stock_allocation_request_id = fields.Many2one('stock.allocation.request', string='Stock Allocation Request',
                                               compute='_compute_allocation_request_id', store=True, index=True)

    @api.constrains('stock_allocation_request_line_ids')
    def _check_allocation_request_lines(self):
        for r in self:
            if len(r.stock_allocation_request_line_ids.mapped('request_id')) > 1:
                raise ValidationError(_("A single procurement group is not allowed to refer to multiple stock allocation requests."))

    @api.depends('stock_allocation_request_line_ids')
    def _compute_allocation_request_id(self):
        for r in self:
            allocation_request_ids = r.stock_allocation_request_line_ids.mapped('request_id')
            if allocation_request_ids:
                r.stock_allocation_request_id = allocation_request_ids[0]
            else:
                r.stock_allocation_request_id = False
