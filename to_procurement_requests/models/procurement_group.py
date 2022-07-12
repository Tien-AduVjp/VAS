from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    replenishment_request_line_ids = fields.One2many('replenishment.request.line', 'procurement_group_id', string='Replenishment Request Lines')
    replenishment_request_id = fields.Many2one('replenishment.request', string='Replenishment Request',
                                               compute='_compute_replenishment_request_id', store=True, index=True)

    @api.constrains('replenishment_request_line_ids')
    def _check_replenishment_request_lines(self):
        for r in self:
            if len(r.replenishment_request_line_ids.mapped('request_id')) > 1:
                raise ValidationError(_("A single procurement group is not allowed to refer to multiple replenishment requests."))

    @api.depends('replenishment_request_line_ids')
    def _compute_replenishment_request_id(self):
        for r in self:
            replenishment_request_ids = r.replenishment_request_line_ids.mapped('request_id')
            if replenishment_request_ids:
                r.replenishment_request_id = replenishment_request_ids[0]
            else:
                r.replenishment_request_id = False
