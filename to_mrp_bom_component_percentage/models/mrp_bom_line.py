from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_compare


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    price_percent = fields.Float(string='Price Percentage (%)', help="Price Percentage of this component in bom.")

    @api.constrains('price_percent')
    def _check_nagative_price_percent(self):
        for r in self:
            if float_compare(r.price_percent, 0.0, precision_digits=2) == -1:
                raise ValidationError(_('Price percentage should not be negative.'))


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.constrains('bom_line_ids')
    def _check_valid_price_percentage(self):
        for r in self:
            total_percent = sum(r.bom_line_ids.mapped('price_percent'))
            if float_compare(total_percent, 100, precision_digits=2) != 0 and not float_is_zero(total_percent, precision_digits=2):
                raise ValidationError(_('Sum of price percentage of all the BoM lines should be equal to 100.'))
            if not float_is_zero(total_percent, precision_digits=2) and any(float_is_zero(line.price_percent, precision_digits=2) for line in r.bom_line_ids):
                raise ValidationError(_('Either all  or none of the BoM lines should be specified with a price percentage'))

