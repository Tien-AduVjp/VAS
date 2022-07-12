from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    product_id = fields.Many2one('product.product', string='Product', copy=True, compute='_compute_product_id', readonly=False, store=True)
    quantity_to_check = fields.Float(string='Qty to Check', compute='_compute_quantity_to_check',
                                     store=True, index=True, help='The quantity for the quality check (in percentage)')
    checked_quantity = fields.Float(string='Checked Quantity', compute='_compute_quantity_to_check', store=True, readonly=False,
                                    help='The total quantity that has been checked (in percentage)')
    checked_qty_deviation = fields.Float(string='Checked Qty Deviation', compute='_compute_checked_qty_deviation', store=True, index=True,
                                         help="The deviation between Qty to Check and Checked Quantity. A Possible Value indecates the checked"
                                         " quantity is more than the quantity that needs to check")

    @api.depends('point_id')
    def _compute_quantity_to_check(self):
        for r in self:
            r.quantity_to_check = r.checked_quantity = r.point_id.quantity_to_check or 100

    @api.constrains('product_id', 'point_id')
    def check_product_vs_point(self):
        for r in self.filtered(lambda r: r.point_id):
            if r.product_id:
                if r.point_id.product_id:
                    if r.point_id.product_id != r.product_id:
                        raise ValidationError(_("The product of the quality check %s must be the same as the product of the corresponding quality point %s")
                                              % (r.name, r.point_id.name))
                elif r.product_id.id not in r.point_id.product_tmpl_id.product_variant_ids.ids:
                    raise ValidationError(_("The product of the quality check %s must be a variant of the product of the corresponding quality point %s")
                                          % (r.name, r.point_id.name))

    @api.depends('quantity_to_check', 'checked_quantity')
    def _compute_checked_qty_deviation(self):
        for r in self:
            r.checked_qty_deviation = r.checked_quantity - r.quantity_to_check

    @api.depends('point_id')
    def _compute_product_id(self):
        for r in self:
            if r.point_id:
                r.product_id = r.point_id.product_id
            else:
                r.product_id = r.product_id

    def _prepare_quality_alert_data(self):
        res = super(QualityCheck, self)._prepare_quality_alert_data()
        res.update({
            'product_id': self.product_id.id,
            'product_tmpl_id': self.product_id.product_tmpl_id.id
            })
        return res
