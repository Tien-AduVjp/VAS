from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class account_move(models.Model):
    _inherit = 'account.move'
    
    custom_declaration_import_id = fields.Many2one('custom.declaration.import', groups="stock.group_stock_user,to_foreign_trade.group_foreign_trade_user", 
                                                   string="Import Custom Declaration", ondelete="restrict", copy=False)
    custom_declaration_export_id = fields.Many2one('custom.declaration.export', groups="stock.group_stock_user,to_foreign_trade.group_foreign_trade_user", 
                                                   string="Export Custom Declaration", ondelete="restrict", copy=False)
    
    
    
    @api.constrains('custom_declaration_import_id', 'custom_declaration_export_id')
    def _constrains_custom_declaration_import_id_custom_declaration_export_id(self):
        for r in self:
            if r.custom_declaration_import_id and r.custom_declaration_export_id:
                raise ValidationError(_('An Account Move cannot link both Import Custom Declaration and Export Custom Declaration'))
