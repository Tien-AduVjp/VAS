from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    custom_declaration_import_id = fields.Many2one('custom.declaration.import', groups="stock.group_stock_user,viin_foreign_trade.group_foreign_trade_user",
                                                   string="Import Custom Declaration", ondelete="restrict")
    custom_declaration_export_id = fields.Many2one('custom.declaration.export', groups="stock.group_stock_user,viin_foreign_trade.group_foreign_trade_user",
                                                   string="Export Custom Declaration", ondelete="restrict")

    @api.constrains('custom_declaration_import_id', 'custom_declaration_export_id')
    def _constrains_custom_declaration_import_id_custom_declaration_export_id(self):
        for r in self:
            if r.custom_declaration_import_id and r.custom_declaration_export_id:
                raise ValidationError(_('An Account Move cannot link both Import Custom Declaration and Export Custom Declaration'))
    
    def button_draft(self):
        self_sudo = self.sudo()
        for move in self_sudo:
            if move.custom_declaration_import_id and move.custom_declaration_import_id.state == 'done':
                move.custom_declaration_import_id.state = 'confirm'
            elif move.custom_declaration_export_id and move.custom_declaration_export_id.state == 'done':
                move.custom_declaration_export_id.state = 'confirm'
        return super(AccountMove, self).button_draft()
    
    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        self_sudo = self.sudo()
        posted_move = self_sudo.filtered(lambda m: m.state == 'posted')
        for r in posted_move:
            if r.custom_declaration_import_id.is_paid:
                r.custom_declaration_import_id.action_done()
            elif r.custom_declaration_export_id.is_paid:
                r.custom_declaration_export_id.action_done()
        return res
