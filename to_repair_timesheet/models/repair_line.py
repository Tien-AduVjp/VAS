from odoo import api, fields, models


class RepairLine(models.Model):
    _inherit = "repair.line"

    invoice_status = fields.Selection([
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string='Invoice Status', compute='_compute_invoice_status', store=True, readonly=True, default='no')

    @api.depends('repair_id.state', 'repair_id.create_invoice', 'invoice_line_id')
    def _compute_invoice_status(self):
        for r in self:
            if r.repair_id.state in ('draft', 'cancel') or not r.repair_id.create_invoice:
                r.invoice_status = 'no'
            elif not r.invoice_line_id:
                r.invoice_status = 'to invoice'
            elif r.invoice_line_id:
                r.invoice_status = 'invoiced'
            else:
                r.invoice_status = 'no'
