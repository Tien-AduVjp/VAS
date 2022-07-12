from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking.type'

    return_reason_required = fields.Boolean(string='Return Reason Required', default=False, help="If checked, return pickings"
                                            " of this type will require a return reason to be specified")
