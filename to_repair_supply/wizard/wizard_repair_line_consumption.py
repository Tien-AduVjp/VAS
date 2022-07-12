from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare

class WizardRepairLineConsumption(models.TransientModel):
    _name = 'wizard.repair.line.consumption'
    _description = 'Repair Line Consumption Wizard'

    wizard_id = fields.Many2one('wizard.repair.order.consumption', string='Repair Order Consumption Wizard', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', readonly=True, required=True)
    name = fields.Text(string='Description', readonly=True, required=True)
    lot_id = fields.Many2one('stock.production.lot', string='Lot/Serial', readonly=True)
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', readonly=True, required=True)
    consumed_qty = fields.Float(string='Consumed Quantity', digits='Product Unit of Measure', readonly=True)
    request_qty = fields.Float(string='Request Quantity', digits='Product Unit of Measure')
    repair_line_id = fields.Many2one('repair.line', string='Repair Line', readonly=True, required=True)
    should_update_quantity = fields.Boolean(string='Update Quantity on RO')
    can_update = fields.Boolean(string='Can Update', compute='_compute_can_update')

    @api.constrains('request_qty')
    def _check_request_qty(self):
        for r in self:
            if r.lot_id and r.product_id.tracking == 'serial' and r.request_qty + r.consumed_qty > 1:
                raise ValidationError(_(" A serial number should only be linked to a single product."))

    @api.depends('request_qty', 'product_uom_qty', 'consumed_qty')
    def _compute_can_update(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for r in self:
            if float_compare(r.request_qty + r.consumed_qty, r.product_uom_qty, precision_digits=precision) > 0:
                r.can_update = True
            else:
                r.can_update = False
                r.should_update_quantity = False
