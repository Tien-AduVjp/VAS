from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FeeDefinition(models.Model):
    _name = 'fee.definition'
    _inherit = 'mail.thread'
    _description = 'Fee Definition'
    _rec_name = 'product_id'

    @api.model
    def _get_default_currency(self):
        return self.env.company.currency_id

    product_tmpl_id = fields.Many2one('product.template', string='Applied to', required=True, index=True, tracking=True,
                                      help="The product template to which this fee definition may apply.")

    product_id = fields.Many2one('product.product', string='Fee Product', required=True, index=True, tracking=True,
                                 help="The product presenting this fee definition for accounting integration (i.e. used in invoicing the fee)",
                                 domain=[('type', '=', 'service')])

    quantity = fields.Float(string='Quantity', required=True, digits='Product Unit of Measure', default=1,
                            tracking=True)
    uom_id = fields.Many2one('uom.uom', string='Product Uom', tracking=True,
                                     related='product_id.uom_id', store=True, readonly=True,
                                     help="The unit of measure which is related to the selected product's default unit of measure.")

    @api.constrains('product_id','product_tmpl_id')
    def _check_contrains_direct_fee_nested_fee(self):
        for r in self:
            if r.product_id.product_tmpl_id == r.product_tmpl_id:
                raise ValidationError(_("The product representing fee '%s' must be different from the product this fee may be applied.") % r.product_id.name)
