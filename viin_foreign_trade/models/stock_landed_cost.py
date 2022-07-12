from odoo import models, fields, _
from odoo.exceptions import UserError


class StockLandedCost(models.AbstractModel):
    _inherit = 'stock.landed.cost'

    custom_declaration_import_id = fields.Many2one('custom.declaration.import', string="Custom Clearance Import Request")
    custom_declaration_export_id = fields.Many2one('custom.declaration.export', string="Custom Clearance Export Request")

    def compute_landed_cost(self):
        if self.mapped('custom_declaration_import_id') or self.mapped('custom_declaration_export_id'):
            raise UserError(_('This landed cost was generated from custom declaration, so you can not recompute it.'))
        else:
            return super(StockLandedCost, self).compute_landed_cost()

    def _check_sum(self):
        if self.mapped('custom_declaration_import_id') or self.mapped('custom_declaration_export_id'):
            return True
        else:
            return super(StockLandedCost, self)._check_sum()

    def button_validate(self):
        """
        We need to implement this method to prevent account move of stock landed cost is linked to custom declaration
        due to default value in context
        """
        if self._context.get('default_custom_declaration_import_id', False):
            self = self.with_context({'default_custom_declaration_import_id': False})

        if self._context.get('default_custom_declaration_export_id', False):
            self = self.with_context({'default_custom_declaration_export_id': False})

        return super(StockLandedCost, self).button_validate()
