from odoo import models, fields


class InstallModuleWarningWizard(models.TransientModel):
    _name = 'install.module.warning.wizard'
    _description = 'Install Modules Warning Wizard'

    module_ids = fields.Many2many('ir.module.module', string='Modules')

    def action_continue_install(self):
        module_ids = self._context.get('active_ids', [])
        modules = self.env['ir.module.module'].browse(module_ids)
        return modules.with_context(skip_warning=True).button_immediate_install()
