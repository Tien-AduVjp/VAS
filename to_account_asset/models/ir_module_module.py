from odoo import models, _
from odoo.exceptions import UserError


class IrModule(models.Model):
    _inherit = 'ir.module.module'

    def button_immediate_install(self):
        if 'account_asset' in self.mapped('name'):
            raise UserError(_("You must uninstall the module `to_account_asset` before you could install the module `account_asset`."))
        return super(IrModule, self).button_immediate_install()
