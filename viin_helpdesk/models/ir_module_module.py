from odoo import models, _
from odoo.exceptions import UserError


class IrModule(models.Model):
    _inherit = 'ir.module.module'

    def button_immediate_install(self):
        if 'helpdesk' in self.mapped('name'):
            raise UserError(_("You must uninstall the module `viin_helpdesk` before you could install the module `helpdesk`."))
        return super(IrModule, self).button_immediate_install()
